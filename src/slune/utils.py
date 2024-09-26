import os
from typing import List, Optional, Tuple

def find_directory_path(strings: List[str], root_directory: Optional[str]='.') -> Tuple[int, str]:
    """ Searches the root directory for a path of directories that matches the strings given in any order.
    If only a partial match is found, returns the deepest matching path.
    If no matches are found returns root_directory.
    Returns a stripped matching path of directories, ie. where we convert '--string=value' to '--string='.

    Args:
        - strings (list of str): List of strings to be matched in any order. Each string in list must be in the form '--string='.
        - root_directory (string, optional): Path to the root directory to be searched, default is current working directory.
    
    Returns:
        - max_depth (int): Depth of the deepest matching path.
        - max_path (string): Path of the deepest matching path.
    
    """

    def _find_directory_path(curr_strings, curr_root, depth, max_depth, max_path):
        dir_list = [entry.name for entry in os.scandir(curr_root) if entry.is_dir()]
        stripped_dir_list = [d.split('=')[0].strip() +"=" for d in dir_list]
        stripped_dir_list = list(set(stripped_dir_list))
        for string in curr_strings:
            if string in stripped_dir_list:
                dir_list = [d for d in dir_list if d.startswith(string)]
                for d in dir_list:
                    new_depth, new_path = _find_directory_path([s for s in curr_strings if s != string], os.path.join(curr_root, d), depth + 1, max_depth, max_path)
                    if new_depth > max_depth:
                        max_depth, max_path = new_depth, new_path
        if depth > max_depth:
            max_depth, max_path = depth, curr_root
        return max_depth, max_path

    max_depth, max_path = _find_directory_path(strings, root_directory, 0, -1, '')
    if max_depth > 0:
        max_path = max_path[len(root_directory):]
        dirs = max_path[1:].split(os.path.sep)
        dirs = [d.split('=')[0].strip() +"=" for d in dirs]
        max_path = os.path.join(*dirs)
        max_path = os.path.join(root_directory, max_path)
    return max_path

def get_numeric_equiv(og_path: str, root_directory: Optional[str]='.') -> str:
    """ Replaces directories in path with existing directories with the same numerical value.

    Args:
        - og_path (str): Path we want to check against existing paths, must be a subdirectory of root_directory and each directory must have form '--string=value'.
        - root_directory (str, optional): Path to the root directory to be searched, default is current working directory.
    
    Returns:
        - equiv (str): Path with values changed to match existing directories if values are numerically equivalent, with root directory at beginning.

    """

    def is_numeric(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    dirs = og_path.split(os.path.sep)
    equiv = root_directory
    for d in dirs:
        next_dir = os.path.join(equiv, d)
        if os.path.exists(next_dir):
            equiv = next_dir
        else:
            if not '=' in d: # We only consider directories with the form '--string=value'
                equiv = next_dir
                continue
            # If the directory doesn't exist, check if there's a directory with the same numerical value
            dir_value = d.split('=')[1]
            if is_numeric(dir_value):
                dir_value = float(dir_value)
                if os.path.exists(equiv):
                    existing_dirs = [entry.name for entry in os.scandir(equiv) if entry.is_dir()]
                    for existing_dir in existing_dirs:
                        if not '=' in existing_dir: # We only consider directories with the form '--string=value'
                            continue
                        existing_dir_value = existing_dir.split('=')[1]
                        if is_numeric(existing_dir_value) and float(existing_dir_value) == dir_value:
                            equiv = os.path.join(equiv, existing_dir)
                            break
                    # If there is no directory with the same numerical value 
                    # we just keep the directory as is and move on to the next one
                    else:
                        equiv = next_dir
                else:
                    # If the directory doesn't exist we just keep the directory as is and move on to the next one
                    equiv = next_dir
            # Otherwise we just keep the directory as is and move on to the next one
            else:
                equiv = next_dir
    return equiv

def dict_to_strings(d: dict, ready_for_cl: bool=False) -> List[str]:
    """ Converts a dictionary into a list of strings in the form of 'key=value'.

    Converts a dictionary into a list of strings in the form of 'key=value' or 'key' if the value is None.

    Args:
        - d (dict): Dictionary to be converted.
        - ready_for_cl (bool, optional): If True adds '--' to the beginning of each key to make ready for running scripts from command-line, default is False.

    Returns:
        - out (list of str): List of strings in the form of 'key=value'/'key'.

    """

    out = []
    if d in [{}, None]:
        return out
    for key, value in d.items():
        if '=' in key:
            raise ValueError("Keys cannot contain '='")
        elif '=' in str(value):
            raise ValueError("Values cannot contain '='")
        elif ready_for_cl:
            if value == None:
                out.append('--{}'.format(key))
            else:
                out.append('--{}={}'.format(key, value))
        else:
            if value == None:
                out.append('{}'.format(key))
            else:
                out.append('{}={}'.format(key, value))
    return out

def strings_to_dict(ls:List[str])->dict:
    """ Converts a list of strings in the form of 'key=value' into a dictionary.

    If the key starts with '--' or '-', it is stripped of these characters. Helpful when converting command line arguments into a dictionary.

    Args:
        - ls (list of str): List of strings in the form of 'key=value'.

    Returns:
        - d (dict): Dictionary containing the key-value pairs.

    """
    d = {}
    for item in ls:
        if item.count('=') != 1:
            raise ValueError("Each string in the list must contain exactly one '=' between the key and value.")
        key, value = item.split('=')
        if key[:2] == '--':
            key = key[2:]
        elif key[0] == '-':
            key = key[1:]
        # Attempt to convert value to int or float
        if ('.' in value) or ('e' in value):
            try:
                value = float(value)
            except ValueError:
                pass
        else:
            try:
                value = int(value)
            except ValueError:
                pass
        d[key] = value
    return d

def find_ext_files(ext: str, root_directory: Optional[str]='.') -> List[str]:
    """ Recursively finds all files with 'ext' extension in all subdirectories of the root directory and returns their paths.

    Args:
        - ext (str): Extension of the files we want to find.
        - root_directory (str, optional): Path to the root directory to be searched, default is current working directory.

    Returns:
        - files (list of str): List of strings containing the paths to all files with ext as the extension found.

    """
    ext_files = []
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith(ext):
                ext_files.append(os.path.join(root, file))
    return ext_files

def get_all_paths(ext:str, dirs: List[str], root_directory: Optional[str]='.') -> List[str]:
    """ Find all possible paths of files with 'ext' extension that have directory matching one of each of all the parameters given.
    
    Finds all paths of files ending with 'ext' in all subdirectories of the root directory that have a directory in their path matching one of each of all the parameters given.

    Args:
        - ext (str): Extension of the files we want to find.
        - dirs (list of str): List of directory names we want returned paths to have in their path. Checks equivalence of values if the directory name is in the form '--string=value'.
        - root_directory (str, optional): Path to the root directory to be searched, default is current working directory.

    Returns:
        - matches (list of str): List of strings containing the paths to all files ending with 'ext' found.

    """

    all_files = find_ext_files(ext, root_directory)
    matches = []
    for file in all_files:
        path = file.split(os.path.sep)
        contains = []
        if dirs in [None, []]:
            matches.append(file)
            continue
        else:
            for p in dirs:
                if '=' in p:
                    param, value = p.split('=')
                    for dir in path:
                        if dir.startswith(param + '='):
                            _, dir_value = dir.split('=')
                            try:
                                if float(value) == float(dir_value):
                                    contains.append(p)
                            except ValueError:
                                if value == dir_value:
                                    contains.append(p)
                elif p in path:
                    contains.append(p)
            if len(contains) == len(dirs):
                matches.append(file)
    return matches