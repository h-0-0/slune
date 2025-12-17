import unittest
from slune.searchers.grid import SearcherGrid
from slune.base import BaseSaver, BaseLogger

class MockLogger(BaseLogger):
    def __init__(self):
        super(MockLogger, self).__init__()
    
    def log(self):
        return 1

    def read_log(self):
        return 1

class MockSaver(BaseSaver):
    def __init__(self, logger_instance: BaseLogger):
        super(MockSaver, self).__init__(logger_instance)
    
    def save_collated(self, *args, **kwargs):
        return 1
    
    def read(self, *args, **kwargs):
        return 1

    def exists(self, params):
        # Mock exists method
        return 0

class TestSearcherGridCheckExisting(unittest.TestCase):
    """Test SearcherGrid.check_existing_runs() method in isolation"""

    def test_check_with_valid_saver(self):
        """Check with valid saver: Should set saver_exists attribute correctly"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        # Initially saver_exists should be None
        self.assertIsNone(searcher.saver_exists)
        
        # Call check_existing_runs
        saver = MockSaver(MockLogger())
        searcher.check_existing_runs(saver)
        
        # saver_exists should be set and callable
        self.assertIsNotNone(searcher.saver_exists)
        self.assertTrue(callable(searcher.saver_exists))

    def test_check_with_runs_zero(self):
        """Check with runs=0: Should raise ValueError"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=0)
        
        saver = MockSaver(MockLogger())
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            searcher.check_existing_runs(saver)

    def test_saver_exists_is_callable(self):
        """Verify saver_exists is callable after setup"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        saver = MockSaver(MockLogger())
        searcher.check_existing_runs(saver)
        
        # Should be callable
        self.assertTrue(callable(searcher.saver_exists))
        
        # Should be able to call it
        result = searcher.saver_exists({"--param1": 1, "--param2": "a"})
        self.assertEqual(result, 0)  # Mock returns 0

    def test_saver_exists_points_to_saver_exists_method(self):
        """Test that saver_exists points to saver.exists method"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        saver = MockSaver(MockLogger())
        searcher.check_existing_runs(saver)
        
        # saver_exists should be the same as saver.exists
        self.assertEqual(searcher.saver_exists, saver.exists)


if __name__ == '__main__':
    unittest.main()
