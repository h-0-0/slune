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
            # If the directory doesn't exist, check if there's a directory with the same numerical value
            dir_value = d.split('=')[1]
            if is_numeric(dir_value):
                dir_value = float(dir_value)
                if os.path.exists(equiv):
                    existing_dirs = [entry.name for entry in os.scandir(equiv) if entry.is_dir()]
                    for existing_dir in existing_dirs:
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

def dict_to_strings(d: dict) -> List[str]:
    """ Converts a dictionary into a list of strings in the form of '--key=value'.

    Args:
        - d (dict): Dictionary to be converted.

    Returns:
        - out (list of str): List of strings in the form of '--key=value'.

    """

    out = []
    for key, value in d.items():
        if key.startswith('--'):
            out.append('{}={}'.format(key, value))
        else:
            out.append('--{}={}'.format(key, value))
    return out

def find_csv_files(root_directory: Optional[str]='.') -> List[str]:
    """ Recursively finds all csv files in all subdirectories of the root directory and returns their paths.

    Args:
        - root_directory (str, optional): Path to the root directory to be searched, default is current working directory.

    Returns:
        - csv_files (list of str): List of strings containing the paths to all csv files found.

    """
    csv_files = []
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files

def get_all_paths(dirs: List[str], root_directory: Optional[str]='.') -> List[str]:
    """ Find all possible paths of csv files that have directory matching one of each of all the parameters given.
    
    Finds all paths of csv files in all subdirectories of the root directory that have a directory in their path matching one of each of all the parameters given.

    Args:
        - dirs (list of str): List of directory names we want returned paths to have in their path.
        - root_directory (str, optional): Path to the root directory to be searched, default is current working directory.

    Returns:
        - matches (list of str): List of strings containing the paths to all csv files found.

    """

    all_csv = find_csv_files(root_directory)
    matches = []
    for csv in all_csv:
        path = csv.split(os.path.sep)
        if all([p in path for p in dirs]):
            matches.append(csv)
    return matches