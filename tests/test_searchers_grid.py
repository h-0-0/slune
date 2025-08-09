import unittest

# Import your SearcherGrid class here
from slune.searchers.grid import SearcherGrid
from slune.base import BaseSaver, BaseLogger

# Create a mock Logger object to use in the tests
class MockLogger(BaseLogger):
    def __init__(self):
        super(MockLogger, self).__init__()
    
    def log(self):
        return 1

    def read_log(self):
        return 1

# Create a mock Saver object to use in the tests
class MockSaver(BaseSaver):
    def __init__(self, logger_instance: BaseLogger):
        super(MockSaver, self).__init__(logger_instance)
        self.runs = 2
        self.grid = [
            {"--param1": 1, "--param2": "a"},
            {"--param1": 1, "--param2": "b"},
            {"--param1": 2, "--param2": "a"},
            {"--param1": 2, "--param2": "b"}
        ]
    
    def save_collated(self, *args, **kwargs):
        return 1
    
    def read(self, *args, **kwargs):
        return 1

    def exists(self, params):
        # Accept dicts from SearcherGrid.exists calls
        return 1 if isinstance(params, dict) and params.get("--param1") == 1 else 0

class TestSearcherGrid(unittest.TestCase):

    def test_get_grid(self):
        # Test that get_grid returns the expected list of dictionaries
        
        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters)
        
        # Get the grid of hyperparameters
        grid = searcher.grid
        
        # Check if the length of the grid is as expected
        self.assertEqual(len(grid), 4)  # 2 values for param1 x 2 values for param2
        
        # Check if the grid contains the expected dictionaries
        expected_grid = [
            {"--param1": 1, "--param2": "a"},
            {"--param1": 1, "--param2": "b"},
            {"--param1": 2, "--param2": "a"},
            {"--param1": 2, "--param2": "b"}
        ]
        self.assertEqual(grid, expected_grid)

    def test_next_tune(self):
        # Test that next_tune returns the expected combinations of hyperparameters
        
        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters)
        
        # Test the first few calls to next_tune
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'a'})
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'b'})
        self.assertEqual(searcher.next_tune(), {'--param1':2, '--param2':'a'})
        self.assertEqual(searcher.next_tune(), {'--param1':2, '--param2':'b'})
        
        # Test that it raises IndexError when all combinations are exhausted
        with self.assertRaises(IndexError):
            searcher.next_tune()

    def test__len__(self):
        # Test that __len__ returns the expected number of hyperparameter combinations
        
        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=1)
        
        # Check that the length is as expected
        self.assertEqual(len(searcher), 4)

    def test_runs_positive(self):
        # Test that when we set the number of runs to a positive integer, next_tune returns the expected combinations of hyperparameters

        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)

        # Test the first few calls to next_tune
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'a'})
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'a'})
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'b'})
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'b'})
        self.assertEqual(searcher.next_tune(), {'--param1':2, '--param2':'a'})

    def test_runs_zero(self):
        # Test that when we set the number of runs to zero, next_tune runs one of each run and then raises IndexError

        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=0)

        # Test all calls to next_tune
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'a'})
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'b'})
        self.assertEqual(searcher.next_tune(), {'--param1':2, '--param2':'a'})
        self.assertEqual(searcher.next_tune(), {'--param1':2, '--param2':'b'})
        with self.assertRaises(IndexError):
            searcher.next_tune()
    
    def test_check_existing_runs(self):
        # Test that check_existing_runs correctly sets the saver_exists attribute
        
        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=1)
        
        # Check that saver_exists is None before calling check_existing_runs
        self.assertIsNone(searcher.saver_exists)
        
        # Check that saver_exists is set to a function after calling check_existing_runs
        searcher.check_existing_runs(MockSaver(MockLogger()))
        self.assertTrue(callable(searcher.saver_exists))
    
    def test_skip_existing_runs_positive(self):
        # Test that skip_existing_runs correctly skips existing runs
        
        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=1)
        
        # Check that skip_existing_runs correctly skips existing runs
        searcher.check_existing_runs(MockSaver(MockLogger()))
        self.assertEqual(searcher.skip_existing_runs(0), (2, 0))
        self.assertEqual(searcher.skip_existing_runs(1), (2, 0))
        self.assertEqual(searcher.skip_existing_runs(2), (2, 0))
        self.assertEqual(searcher.skip_existing_runs(3), (3, 0))
        with self.assertRaises(IndexError):
            searcher.skip_existing_runs(4)
    
    def test_skip_existing_runs_with_runs_zero(self):
        # Test that skip_existing_runs correctly skips existing runs
        
        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=0)
        
        # Check that skip_existing_runs correctly skips existing runs
        with self.assertRaises(ValueError):
            searcher.check_existing_runs(MockSaver(MockLogger()))
        self.assertEqual(searcher.skip_existing_runs(0), (0, 0))
        self.assertEqual(searcher.skip_existing_runs(1), (1, 0))
        self.assertEqual(searcher.skip_existing_runs(2), (2, 0))
        self.assertEqual(searcher.skip_existing_runs(3), (3, 0))
        with self.assertRaises(IndexError):
            searcher.skip_existing_runs(4)      

    def test_next_tune_with_check_existing_runs(self):
        # Test that next_tune correctly skips existing runs
        
        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        # Check that next_tune correctly skips existing runs
        searcher.check_existing_runs(MockSaver(MockLogger()))
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'a'})
        self.assertEqual(searcher.next_tune(), {'--param1':1, '--param2':'b'})
        self.assertEqual(searcher.next_tune(), {'--param1':2, '--param2':'a'})
        self.assertEqual(searcher.next_tune(), {'--param1':2, '--param2':'a'})
        self.assertEqual(searcher.next_tune(), {'--param1':2, '--param2':'b'})
        self.assertEqual(searcher.next_tune(), {'--param1':2, '--param2':'b'})
        with self.assertRaises(IndexError):
            searcher.next_tune()

    def test_iterating_with_next_tune_with_check_existing_runs(self):
        # Test that iterating through SearcherGrid correctly skips existing runs
        
        # Create an instance of SearcherGrid with sample hyperparameters
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"],
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        # Assert that when iterating through SearcherGrid correctly skips existing runs
        searcher.check_existing_runs(MockSaver(MockLogger()))
        for config in searcher:
            self.assertTrue(config in [{'--param1':1, '--param2':'a'}, {'--param1':1, '--param2':'b'}, {'--param1':2, '--param2':'a'}, {'--param1':2, '--param2':'b'}])


    def test_non_list_values_in_configs(self):
        # param values must be iterable; a scalar should raise
        hyperparameters = {
            "--param1": 1,  # not a list/iterable of values
            "--param2": ["a", "b"]
        }
        with self.assertRaises(TypeError):
            SearcherGrid(hyperparameters)

    def test_empty_value_list_results_in_empty_grid(self):
        hyperparameters = {
            "--param1": [],
            "--param2": ["a"]
        }
        searcher = SearcherGrid(hyperparameters, runs=1)
        self.assertEqual(len(searcher), 0)
        with self.assertRaises(IndexError):
            searcher.next_tune()


if __name__ == '__main__':
    unittest.main()
