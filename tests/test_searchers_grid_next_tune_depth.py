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
        params_key = tuple(sorted(params.items()))
        return self.exact_depth_counts.get(params_key, 0)

class TestSearcherGridNextTuneDepth(unittest.TestCase):
    """Test SearcherGrid.next_tune() method with depth issues"""

    def test_next_tune_with_shallow_files(self):
        """Should not skip configs based on shallow files"""
        hyperparameters = {
            "--param1": [1],
            "--param2": ["a"],
            "--param3": ["x"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        # Mock saver returns 0 for exact depth (3 params)
        # This simulates the fix where shallow files don't count
        config = tuple(sorted({"--param1": 1, "--param2": "a", "--param3": "x"}.items()))
        mock_counts = {
            config: 0,  # No exact depth files
        }
        saver = MockSaverExactDepth(MockLogger(), exact_depth_counts=mock_counts)
        searcher.check_existing_runs(saver)
        
        # Should not skip - should return the config
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": "a", "--param3": "x"})

    def test_next_tune_with_exact_depth_files(self):
        """Should skip configs that have enough runs at exact depth"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        # Mock saver returns 2 for first config (enough runs, should skip)
        config1 = tuple(sorted({"--param1": 1, "--param2": "a"}.items()))
        config2 = tuple(sorted({"--param1": 1, "--param2": "b"}.items()))
        mock_counts = {
            config1: 2,  # Enough runs, skip
            config2: 0,  # No runs, don't skip
        }
        saver = MockSaverExactDepth(MockLogger(), exact_depth_counts=mock_counts)
        searcher.check_existing_runs(saver)
        
        # First call should skip config1 and return config2
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": "b"})

    def test_next_tune_with_partial_runs(self):
        """Should continue with remaining runs for configs with partial exact depth matches"""
        hyperparameters = {
            "--param1": [1],
            "--param2": ["a"]
        }
        searcher = SearcherGrid(hyperparameters, runs=3)
        
        # Mock saver returns 1 for config (partial runs)
        config = tuple(sorted({"--param1": 1, "--param2": "a"}.items()))
        mock_counts = {
            config: 1,  # 1 run exists, need 3
        }
        saver = MockSaverExactDepth(MockLogger(), exact_depth_counts=mock_counts)
        searcher.check_existing_runs(saver)
        
        # Should return the config (not skip, since only 1/3 runs exist)
        # run_index starts at 1 (since run 0 already exists, need runs 1 and 2)
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": "a"})
        
        # Next call should return same config (incrementing run_index to 2)
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": "a"})
        
        # After second call, run_index is 2, which is runs-1 (3-1=2)
        # So next call will try to move to next config, but there's only 1 config
        # So it should raise IndexError
        with self.assertRaises(IndexError):
            searcher.next_tune()

    def test_iteration_through_grid_with_mixed_depth_scenarios(self):
        """Test iteration through grid with mixed depth scenarios"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a"],
            "--param3": ["x", "y"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        # Different scenarios:
        # Config 1: enough runs (skip)
        # Config 2: partial runs (continue)
        # Config 3: no runs (start from beginning)
        # Config 4: enough runs (skip)
        config1 = tuple(sorted({"--param1": 1, "--param2": "a", "--param3": "x"}.items()))
        config2 = tuple(sorted({"--param1": 1, "--param2": "a", "--param3": "y"}.items()))
        config3 = tuple(sorted({"--param1": 2, "--param2": "a", "--param3": "x"}.items()))
        config4 = tuple(sorted({"--param1": 2, "--param2": "a", "--param3": "y"}.items()))
        mock_counts = {
            config1: 2,  # Enough runs, skip
            config2: 1,  # Partial runs, continue
            config3: 0,  # No runs, start from beginning
            config4: 2,  # Enough runs, skip
        }
        saver = MockSaverExactDepth(MockLogger(), exact_depth_counts=mock_counts)
        searcher.check_existing_runs(saver)
        
        # Grid order: [param1=1,param2=a,param3=x], [param1=1,param2=a,param3=y], [param1=2,param2=a,param3=x], [param1=2,param2=a,param3=y]
        # Config 0 (param1=1,param2=a,param3=x): has 2 runs (enough), skip to config 1
        # Config 1 (param1=1,param2=a,param3=y): has 1 run (partial), continue at run_index=1
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": "a", "--param3": "y"})
        
        # Next call: run_index was 1, increments to 2. Since runs=2, run_index=2 is not < runs-1 (1)
        # So it moves to next config (config 2)
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 2, "--param2": "a", "--param3": "x"})
        
        # Next call should return config2 again (increment run_index from 0 to 1)
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 2, "--param2": "a", "--param3": "x"})

    def test_next_tune_without_check_existing_runs(self):
        """Test next_tune() without check_existing_runs (should work normally)"""
        hyperparameters = {
            "--param1": [1, 2],
            "--param2": ["a", "b"]
        }
        searcher = SearcherGrid(hyperparameters, runs=2)
        
        # Without check_existing_runs, should work normally
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": "a"})
        
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": "a"})
        
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": "b"})


if __name__ == '__main__':
    unittest.main()
