from typing import Optional, Tuple
import os 
import pandas as pd
from slune.utils import get_all_paths, dict_to_strings
from slune.base import BaseLogger
import random
import time
from .ext import SaverExt

class SaverCsv(SaverExt):
    """ Saves the results of each run in a .csv file in hierarchy of directories.

    Inherits from SaverExt, which coordinates path generation for saving and reading files in a directory hierarchy.
    Please refer to the documentation of SaverExt for more information on how these paths are generated.

    # Saving results
    To save results collated in the logger to a csv file, use the save_collated method. Simply call saver.save_collated().

    # Reading results
    To read the best value of a metric from the csv files in the root directory, use the 'read' method.
    Give it the parameter-value pairs you would like to be included in the search (eg.{'alpha':1}), the metric name (eg.'accuracy'), and how to return a value based on the metric (eg.'max').
    Refer to the methods documentation for more information on how to use it.
     
    Attributes:
        - root_dir (str): Path to the root directory where we will store the csv files.
        - current_path (str): Path to the csv file where we will store the results for the current run.

    """

    def __init__(self, logger_instance: BaseLogger, params: dict = None, root_dir: Optional[str] = os.path.join('.', 'slune_results')):
        """ Initialises the csv saver. 

        Args:
            - logger_instance (BaseLogger): Instance of a logger class that inherits from BaseLogger.
            - params (dict): (key,value) pairs we would like to use for our methods, default is None.
                If None, we will create a path using the parameters given in the log.
            - root_dir (str, optional): Path to the root directory where we will store the csv files, default is './slune_results'.
        
        """

        super(SaverCsv, self).__init__(logger_instance, '.csv',params=params, root_dir=root_dir)
        self.root_dir = root_dir
        self.current_params = params
        if self.current_params is not None:
            self.current_path = self.get_path(dict_to_strings(self.current_params))
        else:
            self.current_path = None

    def save_collated_from_results(self, results: pd.DataFrame):
        """ Saves results to csv file.
        
        If the csv file already exists, 
        we append the collated results from the logger to the end of the csv file.
        If the csv file does not exist,
        we create it and save the results to it.

        Args:
            - results (pd.DataFrame): Data frame containing the results to be saved.

        """

        # If path does not exist, create it
        # Remove the csv file name from the path
        if self.current_path is None:
            self.get_path(self.current_params)
        dir_path = self.current_path.split(os.path.sep)[:-1]
        dir_path = os.path.join(*dir_path)
        if not os.path.exists(dir_path):
            time.sleep(random.random()) # Wait a random amount of time under 1 second to avoid multiple processes creating the same directory
            os.makedirs(dir_path, exist_ok=True)
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
        
    def read(self, params: dict, metric_name: str, select_by: str ='max', collate_by: str ='mean') -> Tuple[dict, float]:
        """ Finds the min/max value of a metric from all csv files in the root directory that match the parameters given.

        Args:
            - params (dict): Contains (parameter,value) pairs we would like in the run.
                If None or empty dict, we will search through all csv files in the root directory.
            - metric_name (string): Name of the metric to be read.
            - select_by (string, optional): How to select the 'best' value for the metric from a log file, currently can select by 'min' or 'max'.
            - collate_by (bool, optional): What to do with the metrics selected over all runs (with same parameters), default is 'mean'.

        Returns:
            - best_params (dict): Contains the arguments used to get the 'best' value of the metric (determined by select_by).
            - best_value (float): Best value of the metric (determined by select_by).

        """

        #  Get all paths that match the parameters given
        paths = get_all_paths('.csv', dict_to_strings(params), root_directory=self.root_dir)
        # If no paths found, return None
        if paths == []:
            return None, None
        # Read the metric from each path
        values = {}
        # Do averaging for different runs of same params if avg is True, otherwise just read the metric from each path
        if collate_by == 'mean':
            paths_same_params = set([os.path.join(*p.split(os.path.sep)[:-1]) for p in paths])
            for path in paths_same_params:
                runs = get_all_paths('.csv', path.split(os.path.sep), root_directory=self.root_dir)
                cumsum = 0
                for r in runs:
                    df = pd.read_csv(r)
                    cumsum += self.read_log(df, metric_name, select_by)
                avg_of_runs = cumsum / len(runs)
                values[path] = avg_of_runs
        elif collate_by == 'all':
            for path in paths:
                df = pd.read_csv(path)
                # values[os.path.join(*path.split(os.path.sep)[:-1])] = self.read_log(df, metric_name, select_by)
                values[path] = self.read_log(df, metric_name, select_by)
        else:
            raise ValueError(f"collate_by must be 'mean' or 'all', got {collate_by}")
        
        # Format the path into a list of arguments 
        out_params, out_values = [], []
        for key in values.keys():
            value = values[key]
            key = key.replace(self.root_dir, '')
            if key.startswith(os.path.sep):
                key = key[1:]
            key = key.split(os.path.sep)
            if key[-1].startswith('results_'):
                # key = key[:-1]
                # if has .csv, remove it
                if key[-1].endswith('.csv'):
                    key[-1] = key[-1][:-4]
            out_params.append(key)
            out_values.append(value)
        return out_params, out_values
