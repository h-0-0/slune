from typing import List, Tuple
from slune.base import BaseSearcher, BaseSaver
from slune.utils import dict_to_strings

class SearcherGrid(BaseSearcher):
    """ Searcher for grid search.
    
    Given dictionary of parameters and values to try, creates grid of all possible configurations,
    and returns them one by one for each call to next_tune.

    Attributes:
        - configs (dict): Parameters and values to create grid from.
            Structure of dictionary should be: { "--parameter_name" : [Value_1, Value_2, ...], ... }
        - runs (int): Controls search based on number of runs we want for each config.
            if runs > 0 -> run each config 'runs' times.
            if runs = 0 -> run each config once even if it already exists.
            This behavior is modified if we want to (use) check_existing_runs, see methods description.
        - grid (list of dict): List of dictionaries, each containing one combination of argument values.
        - grid_index (int): Index of the current configuration in the grid.
        - saver_exists (function): Pointer to the savers exists method, used to check if there are existing runs.

    """

    def __init__(self, configs: dict, runs: int = 0):
        """ Initialises the searcher.

        Args:
            - configs (dict): Dictionary of parameters and values to try.
                Structure of dictionary should be: { "--parameter_name" : [Value_1, Value_2, ...], ... }
            - runs (int, optional): Controls search based on number of runs we want for each config.
                if runs > 0 -> run each config 'runs' times.
                if runs = 0 -> run each config once even if it already exists.
                This behavior is modified if we want to (use) check_existing_runs, see methods description.

        """

        super().__init__()
        self.runs = runs
        self.configs = configs
        self.grid = self.get_grid(configs)
        self.grid_index = None
        self.saver_exists = None

    def __len__(self):
        """ Returns the number of configurations defined by search space. 
        
        This may not be accurate if we want to (use) check_existing_runs,
        as we may skip configurations, 
        see methods description.

        Returns:
            - num_configs (int): Number of configurations defined by search space.

        """

        return len(self.grid) * self.runs

    def get_grid(self, param_dict: dict) -> List:
        """ Creates search grid.
        
        Generates all possible combinations of values for each argument in the given dictionary using recursion.

        Args:
            - param_dict (dict): A dictionary where keys are argument names and values are lists of values.

        Returns:
            - all_combinations (list): A list of dictionaries, each containing one combination of argument values.
        
        """

        # Helper function to recursively generate combinations
        def generate_combinations(param_names, current_combination, all_combinations):
            if not param_names:
                # If there are no more parameters to combine, add the current combination to the result
                all_combinations.append(dict(current_combination))
                return

            param_name = param_names[0]
            param_values = param_dict[param_name]

            for value in param_values:
                current_combination[param_name] = value
                # Recursively generate combinations for the remaining parameters
                generate_combinations(param_names[1:], current_combination, all_combinations)

        # Start with an empty combination and generate all combinations
        all_combinations = []
        generate_combinations(list(param_dict.keys()), {}, all_combinations)

        return all_combinations

    def check_existing_runs(self, saver: BaseSaver):
        """ We save a pointer to the savers exists method to check if there are existing runs.

        If there are n existing runs:
            n < runs -> run the remaining runs
            n >= runs -> skip all runs
        
        Args:
            - saver (BaseSaver): Pointer to the savers exists method, used to check if there are existing runs.

        """

        if self.runs != 0:
            self.saver_exists = saver.exists
        else:
            raise ValueError("Won't check for existing runs if runs = 0, Set runs > 0.")
    
    def skip_existing_runs(self, grid_index: int) -> Tuple[int, int]:
        """ Skips runs if they are in storage already.
        
        Will check if there are existing runs for the current configuration,
        if there are existing runs we tally them up 
        and skip configs or runs of a config based on the number of runs we want for each config.

        Args:
            - grid_index (int): Index of the current configuration in the grid.

        Returns:
            - grid_index (int): Index of the next configuration in the grid.
            - run_index (int): Index of the next run for the current configuration.
        """
        if self.saver_exists != None:
            # Check if there are existing runs, if so skip them
            existing_runs = self.saver_exists(dict_to_strings(self.grid[grid_index]))
            if self.runs - existing_runs > 0:
                run_index = existing_runs
                return grid_index, run_index
            else:
                grid_index += 1
                run_index = 0
                return self.skip_existing_runs(grid_index)
        else:
            if grid_index == len(self.grid):
                raise IndexError('Reached end of grid, no more configurations to try.')
            return grid_index, 0

    def next_tune(self) -> dict:
        """ Returns the next configuration to try.

        Will skip existing runs if check_existing_runs has been called.
        For more information on how this works check the methods descriptions for check_existing_runs and skip_existing_runs.
        Will raise an error if we have reached the end of the grid.
        To iterate through all configurations, use a for loop like so: 
            for config in searcher: ...
            
        Returns:
            - next_config (dict): The next configuration to try.
        """
        # If this is the first call to next_tune, set grid_index to 0
        if self.grid_index is None:
            self.grid_index = 0
            self.grid_index, self.run_index = self.skip_existing_runs(self.grid_index)
        elif self.run_index < self.runs - 1:
            self.run_index += 1
        else:
            self.grid_index += 1
            self.grid_index, self.run_index = self.skip_existing_runs(self.grid_index)
        # If we have reached the end of the grid, raise an error
        if self.grid_index == len(self.grid):
            raise IndexError('Reached end of grid, no more configurations to try.')
        # Return the next configuration to try
        next_config = dict_to_strings(self.grid[self.grid_index])
        return next_config

