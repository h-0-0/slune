import os 
import pandas as pd
from slune.utils import find_directory_path

class SaverCsv():
    """
    Saves the results of each run in a CSV file in a hierarchical directory structure based on argument names.
    """
    def __init__(self, params, root_dir='./tuning_results'):
        self.root_dir = root_dir
        self.current_path = self.get_path(params)
    
    def strip_params(self, params):
        """
        Strips the argument names from the arguments given by args.
        eg. ["--argument_name=argument_value", ...] -> ["--argument_name=", ...]
        Also gets rid of blank spaces
        """
        return [p.split('=')[0].strip() for p in params]

    def get_match(self, params):
        """
        Searches the root directory for a directory tree that matches the parameters given.
        If only partial matches are found, returns the deepest matching directory with the missing parameters appended.
        If no matches are found creates a path using the parameters.
        """
        # First check if there is a directory with path matching some subset of the arguments
        stripped_params = [p.split('=')[0].strip() +'=' for p in params] # Strip the params of whitespace and everything after the '='
        match = find_directory_path(stripped_params, root_directory=self.root_dir)
        # Check which arguments are missing from the path
        missing_params = [[p for p in params if sp in p][0] for sp in stripped_params if sp not in match]
        # Now we add back in the values we stripped out
        if not (match == self.root_dir):
            match = match.split('/')
            match = [match[0]] + [[p for p in params if m in p][0] for m in match[1:]]
            match = '/'.join(match)
        else:
            match = match.split('/')
        # If there are missing arguments, add them to the path
        if len(missing_params) > 0:
            match = match + missing_params
            match = os.path.join(*match)
        return match

    def get_path(self, params):
        """
        Creates a path using the parameters by checking existing directories in the root directory.
        Check get_match for how we create the path, we then check if results files for this path already exist,
        if they do we increment the number of the results file name that we will use.
        TODO: Add option to dictate order of parameters in directory structure.
        TODO: Return warnings if there exist multiple paths that match the parameters but in a different order, or paths that don't go as deep as others.
        Args:
            - params (list): List of strings containing the arguments used, in form ["--argument_name=argument_value", ...].
        """
        # Check if root directory exists, if not create it
        if not os.path.exists(self.root_dir):
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

    def save_collated(self, results):
        # We add results onto the end of the current results in the csv file if it already exists
        # if not then we create a new csv file and save the results there
        if os.path.exists(self.current_path):
            results = pd.concat([pd.read_csv(self.current_path), results])
            results.to_csv(self.current_path, mode='w', index=False)
        else:
            results.to_csv(self.current_path, index=False)
        
    def read(self, *args, **kwargs):
        # TODO: implement this function
        raise NotImplementedError

