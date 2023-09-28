import os

def find_directory_path(strings, root_directory='.'):
    """
    Searches the root directory for a path of directories that matches the strings given in any order.
    If only a partial match is found, returns the deepest matching directory with the missing strings appended.
    If no matches are found returns the strings as a path.
    Args:
        - strings (list): List of strings to be matched in any order. Each string in list must be in the form '--string='.
        - root_directory (string): Path to the root directory to be searched, default is current working directory.
    # TODO: could probably optimize this function
    """
    def _find_directory_path(strings, curr_root, first_call=False):
        # Get list of directories in root directory
        dir_list = os.listdir(curr_root)
        # Get substring up to and including '=' for each directory name in dir_list, and strip whitespace
        stripped_dir_list = [d.split('=')[0].strip() +"=" for d in dir_list]
        # Get rid of duplicates
        stripped_dir_list = list(set(stripped_dir_list))
        # Check if any of the strings are in the list of directories
        for string in strings:
            if string in stripped_dir_list:
                # If a string is found it means that at the current root there is a directory starting "--string="
                # we now want to find all directories in the root directory that start with "--string=" and search them recursively
                # then we return the path to the deepest directory found
                dir_list = [d for d in dir_list if d.startswith(string)]
                # Recursively search each directory starting with string
                paths = []
                for d in dir_list:
                    paths.append(_find_directory_path(strings, os.path.join(curr_root, d)))
                # Return the deepest directory found, ie. most /'s in path
                return max(paths, key=lambda x: x.count('/'))
        # If no strings are found, return the root directory
        if first_call:
            pass
        else:
            curr_root = curr_root[len(root_directory):]
            dirs = curr_root[1:].split('/')
            dirs = [d.split('=')[0].strip() +"=" for d in dirs]
            curr_root = '/'.join(dirs)
            curr_root = os.path.join(root_directory, curr_root)
        return curr_root
    return _find_directory_path(strings, root_directory, first_call=True)


def dict_to_strings(d):
    """
    Converts a dictionary into a list of strings in the form of '--key=value'.
    """
    out = []
    for key, value in d.items():
        if key.startswith('--'):
            out.append('{}={}'.format(key, value))
        else:
            out.append('--{}={}'.format(key, value))
    return out