from typing import List,  Optional
import os 
from slune.utils import find_directory_path, get_all_paths, get_numeric_equiv, dict_to_strings
from slune.base import BaseSaver, BaseLogger
import random
import time

class SaverExt(BaseSaver):
    """ Saves the results of each run in a file with given extension in hierarchy of directories (Partial implementation).
    
    This class must be given a string denoting the extension of the file where we will store the results.
    We will refer to this extension as '.ext' in the documentation where '.ext' is replaced by the value given for ext when initializing the class. 

    This class only partly implements the BaseSaver class, it only implements the exists method.
    The get_path method can be used to generate save locations for the results of each run.
    By inheriting this class one can then sue the get_path method to implement the save_collated and read methods, 
    we can save and read results to/from '.ext' files stored in a hierarchy of directories. 
    The main logic to implement is how to read, manipulate and save the results in the '.ext' files.

    # Generating paths / Directory Structure
    Each directory is named after a parameter - value pair in the form "--parameter_name=value".
    The paths to '.ext' files then define the configuration under which the results were obtained,
    for example if we only have one parameter "learning_rate" with value 0.01 used to obtain the results,
    to save those results we would create a directory named "--learning_rate=0.01" and save the results in a '.ext' file in that directory.

    If we have multiple parameters, for example "learning_rate" with value 0.01 and "batch_size" with value 32,
    we would create a directory named "--learning_rate=0.01" with a subdirectory named "--batch_size=32",
    and save the results in a '.ext' file in that subdirectory.

    We use this structure to then read the results from the '.ext' files by searching for the directory that matches the parameters we want,
    and then reading the '.ext' file in that directory.

    The order in which we create the directories is determined by the order in which the parameters are given,
    so if we are given ["--learning_rate=0.01", "--batch_size=32"] we would create the directories in the following order:
    "--learning_rate=0.01/--batch_size=32".

    The directory structure generated will also depend on existing directories in the root directory,
    if there are existing directories in the root directory that match some subset of the parameters given,
    we will create the directory tree from the deepest matching directory.

    For example if we only have the following path in the root directory:
    "--learning_rate=0.01/--batch_size=32"
    and we are given the parameters ["--learning_rate=0.01", "--batch_size=32", "--num_epochs=10"],
    we will create the path:
    "--learning_rate=0.01/--batch_size=32/--num_epochs=10".
    on the other hand if we are given the parameters ["--learning_rate=0.02", "--num_epochs=10", "--batch_size=32"],
    we will create the path:
    "--learning_rate=0.02/--batch_size=32/--num_epochs=10".

    # Other Comments
    * Handles parallel runs trying to create the same directories by waiting a random time (under 1 second) before creating the directory. Should work pretty well in practice, however, may occasionally fail if you start a large number of jobs at exactly the same time. 

    Attributes:
        - root_dir (str): Path to the root directory where we will store the '.ext' files.
        - current_path (str): Path to the '.ext' file where we will store the results for the current run.

    """

    def __init__(self, logger_instance: BaseLogger, ext: str = '.csv', params: dict = None, root_dir: Optional[str] = os.path.join('.', 'slune_results')):
        """ Initialises the ext(ension) saver. 

        Args:
            - logger_instance (BaseLogger): Instance of a logger class that inherits from BaseLogger.
            - ext (str): Extension of the file where we will store the results, default is '.csv'.
            - params (dict): (key,value) pairs we would like to use for our methods, default is None.
                If None, we will create a path using the parameters given in the log.
            - root_dir (str, optional): Path to the root directory where we will store the '.ext files, default is './slune_results'.
        
        """

        super(SaverExt, self).__init__(logger_instance)
        self.root_dir = root_dir
        self.current_params = params
        self.ext = ext
        if self.current_params is not None:
            self.current_path = self.get_path(dict_to_strings(self.current_params))
        else:
            self.current_path = None
    
    def strip_params(self, params: List[str]) -> List[str]:
        """ Strips the parameter values.

        Strips the parameter values from the list of parameters given,
        ie. ["--parameter_name=parameter_value", ...] -> ["--parameter_name=", ...]

        Also gets rid of blank spaces.

        Args:
            - params (list of str): List of strings containing the parameters used, in form ["--parameter_name=parameter_value", ...].

        Returns:
            - stripped_params (list of str): List of strings containing the parameters used, in form ["--parameter_name=", ...].

        """

        stripped_params = [p.split('=')[0].strip() for p in params]
        return stripped_params

    def get_match(self, params: List[str]) -> str:
        """ Searches the root directory for a path that matches the parameters given.

        If only partial matches are found, returns the deepest matching directory with the missing parameters appended.
        By deepest we mean the directory with the most parameters matching.
        If no matches are found creates a path using the parameters.
        Creates path using parameters in the order they are given, 
        ie. ["--learning_rate=0.01", "--batch_size=32"] -> "--learning_rate=0.01/--batch_size=32".

        If we find a partial match, we add the missing parameters to the end of the path,
        ie. if we have the path "--learning_rate=0.01" in the root 
        and are given the parameters ["--learning_rate=0.01", "--batch_size=32"],
        we will create the path "--learning_rate=0.01/--batch_size=32".

        Args:
            - params (list of str): List of strings containing the arguments used, in form ["--argument_name=argument_value", ...].

        Returns:
            - match (str): Path to the directory that matches the parameters given.

        """

        # First check if there is a directory with path matching some subset of the arguments
        stripped_params = [p.split('=')[0].strip() +'=' for p in params] # Strip the params of whitespace and everything after the '='
        if len(set(stripped_params)) != len(stripped_params):
            raise ValueError(f"Duplicate parameters found in {stripped_params}")
        match = find_directory_path(stripped_params, root_directory=self.root_dir)
        # Add on missing parameters
        if match == self.root_dir:
            match = os.path.join(*stripped_params)
        else:
            missing_params = [p for p in stripped_params if p not in match]
            if missing_params != []:
                match = [match] + missing_params
                match = os.path.join(*match)
        # Take the root directory out of the match
        match = match.replace(self.root_dir, '')
        if match.startswith(os.path.sep):
            match = match[1:]
        # Now we add back in the values we stripped out
        match = match.split(os.path.sep)
        match = [[p for p in params if m in p][0] for m in match]
        # Check if there is an existing path with the same numerical values, if so use that instead
        match = get_numeric_equiv(os.path.join(*match), root_directory=self.root_dir)
        return match

    def get_path(self, params: List[str]) -> str:
        """ Creates a path using the parameters.
        
        Does this by first checking for existing paths in the root directory that match the parameters given.

        Check get_match for how we create the path, 
        once we have the path we check if there is already a '.ext' file with results in that path,
        if there is we increment the number of the results file name that we will use.

        For example if we get back the path "--learning_rate=0.01/--batch_size=32",
        and there exists a '.ext. file named "results_0.ext" in the final directory,
        we will name our '.ext' file "results_1.ext".

        Args:
            - params (list of str): List of strings containing the arguments used, in form ["--argument_name=argument_value", ...].

        Returns:
            - ext_file_path (str): Path to the '.ext' file where we will store the results for the current run.

        """

        # Check if root directory exists, if not create it
        if not os.path.exists(self.root_dir):
            time.sleep(random.random()) # Wait a random amount of time under 1 second to avoid multiple processes creating the same directory
            os.makedirs(self.root_dir, exist_ok=True)
        # Get path of directory where we should store our '.ext' of results
        dir_path = self.get_match(params)
        # Check if directory exists, if not create it
        if not os.path.exists(dir_path):
            ext_file_number = 0
        # If it does exist, check if there is already an ext file with results,
        # if there is find the name of the last ext file and increment the number
        else:
            ext_files = [f for f in os.listdir(dir_path) if f.endswith(self.ext)]
            if len(ext_files) > 0:
                last_ext_file = max(ext_files)
                # Check that the last '.ext' file starts with "results_"
                if not last_ext_file.startswith('results_'):
                    raise ValueError('Found '+ self.ext +' file in directory that doesn\'t start with "results_"')
                ext_file_number = int(last_ext_file.split('_')[1][:-4]) + 1
            else:
                ext_file_number = 0
        # Create path name for a new ext file where we can later store results
        ext_file_path = os.path.join(dir_path, f'results_{ext_file_number}'+self.ext)
        return ext_file_path    

    def exists(self, params: dict) -> int:
        """ Checks if results already exist in storage.

        Args:
            - params (dict): Contains the parameters used.

        Returns:
            - num_runs (int): Number of runs that exist in storage for the given parameters.

        """

        #  Get all paths that match the parameters given
        params = dict_to_strings(params)
        paths = get_all_paths(self.ext, params, root_directory=self.root_dir)
        return len(paths)

    def getset_current_path(self, params:dict=None, save:bool=True) -> str:
        """ Getter/Setter function for the current_path attribute. 
        If params is not None, we will update the current_params attribute and the current_path attribute.
        If params is None, simply returns the current_path attribute.
        By default will save results to the current_path if it is going to be updated.

        Args:
            - params (dict, optional): (key,value) pairs we would like to use for our methods, default is None.
                If None, we will use the current_params attribute.
        
        Returns:
            - current_path (str): Path to the '.ext' file where we will store the results for the current run.
        
        """
        if params is not None:
            if self.current_path is not None:
                if save:
                    self.save_collated()
            self.current_params = params
            self.current_path = self.get_path(dict_to_strings(self.current_params))
        else:
            if self.current_params is None:
                raise ValueError('SaverExt.current_params is None, please provide parameters to get the current path.')
            elif self.current_path is None:
                raise Exception('SaverExt.current_path is None, please provide parameters to create a path.')
        return self.current_path

