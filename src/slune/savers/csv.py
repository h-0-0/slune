from typing import List,  Optional
import os 
import pandas as pd
from slune.utils import find_directory_path, get_all_paths, get_numeric_equiv
from slune.base import BaseSaver, BaseLogger
import random
import time

class SaverCsv(BaseSaver):
    """ Saves the results of each run in a CSV file in hierarchy of directories.
     
    Each directory is named after a parameter - value pair in the form "--parameter_name=value".
    The paths to csv files then define the configuration under which the results were obtained,
    for example if we only have one parameter "learning_rate" with value 0.01 used to obtain the results,
    to save those results we would create a directory named "--learning_rate=0.01" and save the results in a csv file in that directory.

    If we have multiple parameters, for example "learning_rate" with value 0.01 and "batch_size" with value 32,
    we would create a directory named "--learning_rate=0.01" with a subdirectory named "--batch_size=32",
    and save the results in a csv file in that subdirectory.

    We use this structure to then read the results from the csv files by searching for the directory that matches the parameters we want,
    and then reading the csv file in that directory.

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

    Handles parallel runs trying to create the same directories by waiting a random time (under 1 second) before creating the directory.
    Should work pretty well in practice, however, may occasionally fail depending on the number of jobs launched at the same time. 

    Attributes:
        - root_dir (str): Path to the root directory where we will store the csv files.
        - current_path (str): Path to the csv file where we will store the results for the current run.

    """

    def __init__(self, logger_instance: BaseLogger, params: List[str] = None, root_dir: Optional[str] = os.path.join('.', 'slune_results')):
        """ Initialises the csv saver. 

        Args:
            - logger_instance (BaseLogger): Instance of a logger class that inherits from BaseLogger.
            - params (list, optional): List of strings containing the parameters used, in form ["--parameter_name=parameter_value", ...], default is None.
                If None, we will create a path using the parameters given in the log.
            - root_dir (str, optional): Path to the root directory where we will store the csv files, default is './slune_results'.
        
        """

        super(SaverCsv, self).__init__(logger_instance)
        self.root_dir = root_dir
        if params != None:
            self.current_path = self.get_path(params)
    
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
        once we have the path we check if there is already a csv file with results in that path,
        if there is we increment the number of the results file name that we will use.

        For example if we get back the path "--learning_rate=0.01/--batch_size=32",
        and there exists a csv file named "results_0.csv" in the final directory,
        we will name our csv file "results_1.csv".

        Args:
            - params (list of str): List of strings containing the arguments used, in form ["--argument_name=argument_value", ...].

        Returns:
            - csv_file_path (str): Path to the csv file where we will store the results for the current run.

        """

        # Check if root directory exists, if not create it
        if not os.path.exists(self.root_dir):
            time.sleep(random.random()) # Wait a random amount of time under 1 second to avoid multiple processes creating the same directory
            os.makedirs(self.root_dir)
        # Get path of directory where we should store our csv of results
        dir_path = self.get_match(params)
        # Check if directory exists, if not create it
        if not os.path.exists(dir_path):
            csv_file_number = 0
        # If it does exist, check if there is already a csv file with results,
        # if there is find the name of the last csv file and increment the number
        else:
            csv_files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
            if len(csv_files) > 0:
                last_csv_file = max(csv_files)
                # Check that the last csv file starts with "results_"
                if not last_csv_file.startswith('results_'):
                    raise ValueError('Found csv file in directory that doesn\'t start with "results_"')
                csv_file_number = int(last_csv_file.split('_')[1][:-4]) + 1
            else:
                csv_file_number = 0
        # Create path name for a new csv file where we can later store results
        csv_file_path = os.path.join(dir_path, f'results_{csv_file_number}.csv')
        return csv_file_path

    def save_collated_from_results(self, results: pd.DataFrame):
        """ Saves results to csv file.
        
        If the csv file already exists, 
        we append the collated results from the logger to the end of the csv file.
        If the csv file does not exist,
        we create it and save the results to it.

        Args:
            - results (pd.DataFrame): Data frame containing the results to be saved.

        TODO: 
            - Could be making to many assumptions about the format in which we get the results from the logger,
            should be able to work with any logger.
            We should only be assuming that we are saving results to a csv file. 

        """

        # If path does not exist, create it
        # Remove the csv file name from the path
        dir_path = self.current_path.split(os.path.sep)[:-1]
        dir_path = os.path.join(*dir_path)
        if not os.path.exists(dir_path):
            time.sleep(random.random()) # Wait a random amount of time under 1 second to avoid multiple processes creating the same directory
            os.makedirs(dir_path)
        # If csv file already exists, append results to the end
        if os.path.exists(self.current_path):
            results = pd.concat([pd.read_csv(self.current_path), results])
            results.to_csv(self.current_path, mode='w', index=False)
        # If csv file does not exist, create it
        else:
            results.to_csv(self.current_path, index=False)

    def save_collated(self):
        """ Saves results to csv file. """

        self.save_collated_from_results(self.logger.results)
        
    def read(self, params: List[str], metric_name: str, select_by: str ='max', avg: bool =True) -> (List[str], float):
        """ Finds the min/max value of a metric from all csv files in the root directory that match the parameters given.

        Args:
            - params (list of str): Contains the parameters used, in form ["--parameter_name=parameter_value", ...].
            - metric_name (string): Name of the metric to be read.
            - select_by (string, optional): How to select the 'best' value for the metric from a log file, currently can select by 'min' or 'max'.
            - avg (bool, optional): Whether to average the metric over all runs, default is True.

        Returns:
            - best_params (list of str): Contains the arguments used to get the 'best' value of the metric (determined by select_by).
            - best_value (float): Best value of the metric (determined by select_by).

        """

        #  Get all paths that match the parameters given
        paths = get_all_paths(params, root_directory=self.root_dir)
        if paths == []:
            raise ValueError(f"No paths found matching {params}")
        # Read the metric from each path
        values = {}
        # Do averaging for different runs of same params if avg is True, otherwise just read the metric from each path
        if avg:
            paths_same_params = set([os.path.join(*p.split(os.path.sep)[:-1]) for p in paths])
            for path in paths_same_params:
                runs = get_all_paths(path.split(os.path.sep), root_directory=self.root_dir)
                cumsum = 0
                for r in runs:
                    df = pd.read_csv(r)
                    cumsum += self.read_log(df, metric_name, select_by)
                avg_of_runs = cumsum / len(runs)
                values[path] = avg_of_runs
        else:
            for path in paths:
                df = pd.read_csv(path)
                values[os.path.join(*path.split(os.path.sep)[:-1])] = self.read_log(df, metric_name, select_by)
        # Get the key of the min/max value
        if select_by == 'min':
            best_params = min(values, key=values.get)
        elif select_by == 'max':
            best_params = max(values, key=values.get)
        else:
            raise ValueError(f"select_by must be 'min' or 'max', got {select_by}")
        # Find the best value of the metric from the key
        best_value = values[best_params]
        # Format the path into a list of arguments
        best_params = best_params.replace(self.root_dir, '')
        if best_params.startswith(os.path.sep):
            best_params = best_params[1:]
        best_params = best_params.split(os.path.sep)
        return best_params, best_value       

    def exists(self, params: List[str]) -> int:
        """ Checks if results already exist in storage.

        Args:
            - params (list of str): Contains the parameters used, in form ["--parameter_name=parameter_value", ...].

        Returns:
            - num_runs (int): Number of runs that exist in storage for the given parameters.

        """

        #  Get all paths that match the parameters given
        paths = get_all_paths(params, root_directory=self.root_dir)
        return len(paths)

    def get_current_path(self) -> str:
        """ Getter function for the current_path attribute. 
        
        Returns:
            - current_path (str): Path to the csv file where we will store the results for the current run.
        
        """

        return self.current_path
