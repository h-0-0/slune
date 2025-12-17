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

class MockSaverExactDepth(BaseSaver):
    """Mock saver that returns exact depth counts"""
    def __init__(self, logger_instance: BaseLogger, exact_depth_counts=None):
        super(MockSaverExactDepth, self).__init__(logger_instance)
        # exact_depth_counts: dict mapping config dict to count
        self.exact_depth_counts = exact_depth_counts or {}
    
    def save_collated(self, *args, **kwargs):
        return 1
    
    def read(self, *args, **kwargs):
        return 1

    def exists(self, params):
        # Return count for exact depth match only
        # Convert params to tuple for dict key
        params_key = tuple(sorted(params.items()))
        return self.exact_depth_counts.get(params_key, 0)

class TestSearcherGridSkipExisting(unittest.TestCase):
    """Test SearcherGrid.skip_existing_runs() method in isolation with mock saver"""

    def test_shallow_files_dont_affect_skipping(self):
        """Mock saver returns 0 for exact depth, but files exist at shallow depth → should not skip"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"],
            "--param3": ["x", "y"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        # Mock saver returns 0 for exact depth (3 params)
        # This simulates the fix where exists() only counts exact depth
        mock_counts = {
            tuple(sorted({"--param1": 1, "--param2": "a", "--param3": "x"}.items())): 0,
        }
        saver = MockSaverExactDepth(MockLogger(), exact_depth_counts=mock_counts)
        searcher.check_existing_runs(saver)
        
        # Should not skip - no exact depth files exist
        grid_index, run_index = searcher.skip_existing_runs(0)
        # Should start at grid_index 0, run_index 0 (no skipping)
        self.assertEqual(grid_index, 0)
        self.assertEqual(run_index, 0)

    def test_exact_depth_files_affect_skipping(self):
        """Mock saver returns correct count for exact depth → should skip correctly"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        # Mock saver returns 2 for first config (enough runs, should skip)
        # Returns 1 for second config (partial runs, should continue)
        config1 = tuple(sorted({"--param1": 1, "--param2": "a"}.items()))
        config2 = tuple(sorted({"--param1": 1, "--param2": "b"}.items()))
        mock_counts = {
            config1: 2,  # Enough runs, should skip
            config2: 1,  # Partial runs, should continue
        }
        saver = MockSaverExactDepth(MockLogger(), exact_depth_counts=mock_counts)
        searcher.check_existing_runs(saver)
        
        # First config has 2 runs (enough), should skip to next config
        # The recursive call will also check config 1, which has 1 run, so it will return run_index=1
        grid_index, run_index = searcher.skip_existing_runs(0)
        self.assertEqual(grid_index, 1)  # Skip to next config
        self.assertEqual(run_index, 1)  # Config 1 has 1 run, so start at run 1
        
        # Second config has 1 run (partial), should continue with remaining runs
        grid_index, run_index = searcher.skip_existing_runs(1)
        self.assertEqual(grid_index, 1)  # Stay at same config
        self.assertEqual(run_index, 1)  # Continue with run 1

    def test_partial_runs_at_exact_depth(self):
        """Mock saver returns partial count → should continue with remaining runs"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=3)
        
        # Mock saver returns 1 for first config (partial runs)
        config1 = tuple(sorted({"--param1": 1, "--param2": "a"}.items()))
        mock_counts = {
            config1: 1,  # 1 run exists, need 3, so continue with runs 1, 2
        }
        saver = MockSaverExactDepth(MockLogger(), exact_depth_counts=mock_counts)
        searcher.check_existing_runs(saver)
        
        # Should continue with remaining runs
        grid_index, run_index = searcher.skip_existing_runs(0)
        self.assertEqual(grid_index, 0)  # Stay at same config
        self.assertEqual(run_index, 1)  # Start at run 1 (since run 0 already exists)

    def test_run_index_calculation_exact_depth_only(self):
        """Verify run_index is calculated based on exact depth files only"""
        hyperparameters = {
            "--param1": [1],
            "--param2": ["a"],
            "--param3": ["x"]
        }
        searcher = SearcherGrid(hyperparameters, runs=5)
        
        # Mock saver returns 2 for exact depth (3 params)
        # This simulates the fix where shallow files don't count
        config = tuple(sorted({"--param1": 1, "--param2": "a", "--param3": "x"}.items()))
        mock_counts = {
            config: 2,  # 2 runs at exact depth
        }
        saver = MockSaverExactDepth(MockLogger(), exact_depth_counts=mock_counts)
        searcher.check_existing_runs(saver)
        
        # Should calculate run_index based on exact depth count only
        grid_index, run_index = searcher.skip_existing_runs(0)
        self.assertEqual(grid_index, 0)
        self.assertEqual(run_index, 2)  # Start at run 2 (runs 0 and 1 already exist)

    def test_different_grid_positions_and_run_counts(self):
        """Test with different grid positions and run counts"""
        hyperparameters = {
            "--param1": [1, 2, 3],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=4)
        
        # Different counts for different configs
        config1 = tuple(sorted({"--param1": 1, "--param2": "a"}.items()))
        config2 = tuple(sorted({"--param1": 2, "--param2": "a"}.items()))
        config3 = tuple(sorted({"--param1": 3, "--param2": "a"}.items()))
        mock_counts = {
            config1: 4,  # Enough runs, skip
            config2: 2,  # Partial runs, continue
            config3: 0,  # No runs, start from beginning
        }
        saver = MockSaverExactDepth(MockLogger(), exact_depth_counts=mock_counts)
        searcher.check_existing_runs(saver)
        
        # Config 0: skip (4 runs >= 4 needed)
        # Grid order: [param1=1,param2=a], [param1=1,param2=b], [param1=2,param2=a], [param1=2,param2=b], [param1=3,param2=a], [param1=3,param2=b]
        # Config 0 has 4 runs, skips to config 1 (param1=1,param2=b) which has 0 runs (not in mock), so returns run_index=0
        grid_index, run_index = searcher.skip_existing_runs(0)
        self.assertEqual(grid_index, 1)  # Skip to config 1
        self.assertEqual(run_index, 0)  # Config 1 (param1=1,param2=b) has 0 runs, so start at run 0
        
        # Config 2 (param1=2,param2=a): continue (2 runs < 4 needed)
        # Note: skip_existing_runs(2) will check config 2, which has 2 runs, so start at run 2
        grid_index, run_index = searcher.skip_existing_runs(2)
        self.assertEqual(grid_index, 2)  # Stay at config 2
        self.assertEqual(run_index, 2)  # Start at run 2 (runs 0 and 1 already exist)
        
        # Config 4 (param1=3,param2=a): start from beginning (0 runs)
        grid_index, run_index = searcher.skip_existing_runs(4)
        self.assertEqual(grid_index, 4)  # Stay at config 4
        self.assertEqual(run_index, 0)  # Start at run 0


if __name__ == '__main__':
    unittest.main()
