import unittest

# Import your SearcherGrid class here
from slune.searchers import SearcherGrid

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
        self.assertEqual(searcher.next_tune(), ["--param1=1", "--param2=a"])
        self.assertEqual(searcher.next_tune(), ["--param1=1", "--param2=b"])
        self.assertEqual(searcher.next_tune(), ["--param1=2", "--param2=a"])
        self.assertEqual(searcher.next_tune(), ["--param1=2", "--param2=b"])
        
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
        searcher = SearcherGrid(hyperparameters)
        
        # Check that the length is as expected
        self.assertEqual(len(searcher), 4)

if __name__ == '__main__':
    unittest.main()
