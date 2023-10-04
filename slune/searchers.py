from slune.base import BaseSearcher
from slune.utils import dict_to_strings

class SearcherGrid(BaseSearcher):
    """
    Given dictionary of hyperparameters and values to try, creates grid of all possible hyperparameter configurations,
    and returns them one by one for each call to next_tune.
    Args:
        - hyperparameters (dict): Dictionary of hyperparameters and values to try.
            Structure of dictionary should be: { "--argument_name" : [Value_1, Value_2, ...], ... }
    TODO: Add extra functionality by using nested dictionaries to specify which hyperparameters to try together.
    """
    def __init__(self, hyperparameters: dict):
        super().__init__()
        self.hyperparameters = hyperparameters
        self.grid = self.get_grid(hyperparameters)
        self.grid_index = None

    def __len__(self):
        """
        Returns the number of hyperparameter configurations to try.
        """
        return len(self.grid)

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

    def next_tune(self):
        """
        Returns the next hyperparameter configuration to try.
        """
        # If this is the first call to next_tune, set grid_index to 0
        if self.grid_index is None:
            self.grid_index = 0
        else:
            self.grid_index += 1
        # If we have reached the end of the grid, raise an error
        if self.grid_index == len(self.grid):
            raise IndexError('Reached end of grid, no more hyperparameter configurations to try.')
        # Return the next hyperparameter configuration to try
        return dict_to_strings(self.grid[self.grid_index])
