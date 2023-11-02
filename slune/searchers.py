from slune.base import BaseSearcher, BaseSaver
from slune.utils import dict_to_strings

class SearcherGrid(BaseSearcher):
    """
    Given dictionary of hyperparameters and values to try, creates grid of all possible hyperparameter configurations,
    and returns them one by one for each call to next_tune.
    Args:
        - hyperparameters (dict): Dictionary of hyperparameters and values to try.
            Structure of dictionary should be: { "--argument_name" : [Value_1, Value_2, ...], ... }
        - runs (int): Controls search based on number of runs we want for each hyperparameter config
            runs > 0 -> run each hyperparameter config 'runs' times
            runs = 0 -> run each hyperparameter config once even if it already exists
            this behaviour is modified if we want to (use) check_existing_runs, see methods description
    """
    def __init__(self, hyperparameters: dict, runs: int = 1):
        super().__init__()
        self.runs = runs
        self.hyperparameters = hyperparameters
        self.grid = self.get_grid(hyperparameters)
        self.grid_index = None
        self.slog_exists = None

    def __len__(self):
        """
        Returns the number of hyperparameter configurations to try.
        """
        return len(self.grid) * self.runs

    def get_grid(self, param_dict: dict):
        """
        Generate all possible combinations of values for each argument in the given dictionary using recursion.

        Args:
        param_dict (dict): A dictionary where keys are argument names and values are lists of values.

        Returns:
        list: A list of dictionaries, each containing one combination of argument values.
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

    def check_existing_runs(self, slog: BaseSaver):
        """
        We save a pointer to the savers exists method to check if there are existing runs.
        If there are n existing runs:
            n < runs -> run the remaining runs
            n >= runs -> skip all runs
        """
        if self.runs != 0:
            self.slog_exists = slog.exists
        else:
            raise ValueError("Won't check for existing runs if runs = 0, Set runs > 0.")
    
    def skip_existing_runs(self, grid_index):
        """
        Skips existing runs if they exist, returns the grid_index and run_index of the next hyperparameter configuration to try.
        """
        if self.slog_exists != None:
            # Check if there are existing runs, if so skip them
            existing_runs = self.slog_exists(dict_to_strings(self.grid[grid_index]))
            if self.runs - existing_runs > 0:
                run_index = existing_runs
                return grid_index, run_index
            else:
                grid_index += 1
                run_index = 0
                return self.skip_existing_runs(grid_index)
        else:
            foo = len(self.grid)
            if grid_index == len(self.grid):
                raise IndexError('Reached end of grid, no more hyperparameter configurations to try.')
            return grid_index, 0

    def next_tune(self):
        """
        Returns the next hyperparameter configuration to try.
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
            raise IndexError('Reached end of grid, no more hyperparameter configurations to try.')
        # Return the next hyperparameter configuration to try
        return dict_to_strings(self.grid[self.grid_index])

