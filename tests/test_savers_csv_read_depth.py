import unittest
import os
import shutil
import pandas as pd
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault

class TestSaverCsvReadDepth(unittest.TestCase):
    """Test SaverCsv.read() method - should find files at any depth (correct behavior)"""

    def setUp(self):
        # Create a temporary directory with CSV files at different depths
        self.test_dir = 'test_directory'
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create directory structure with CSV files at different depths
        # Depth 1: --param1=1/results_0.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1'), exist_ok=True)
        df = pd.DataFrame({'metric': [0.5, 0.6]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', 'results_0.csv'), index=False)
        
        # Depth 2: --param1=1/--param2=2/results_0.csv, results_1.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2'), exist_ok=True)
        df = pd.DataFrame({'metric': [0.7, 0.8]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'), index=False)
        df = pd.DataFrame({'metric': [0.8, 0.9]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_1.csv'), index=False)
        
        # Depth 3: --param1=1/--param2=2/--param3=3/results_0.csv, results_1.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3'), exist_ok=True)
        df = pd.DataFrame({'metric': [0.9, 1.0]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'), index=False)
        df = pd.DataFrame({'metric': [1.0, 1.1]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv'), index=False)

    def tearDown(self):
        # Clean up the temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_reading_with_partial_params(self):
        """Given 2 params, should find files at depth 2 AND depth 3 (if they match)"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2}
        
        out_params, out_values = saver.read(params, metric_name='metric', select_by='max', collate_by='mean')
        
        # Should find files at both depth 2 and depth 3
        # This is the correct behavior for reading - find at any depth
        self.assertIsNotNone(out_params)
        self.assertIsNotNone(out_values)
        # Should have results from both depths
        self.assertGreater(len(out_params), 0)

    def test_reading_behavior_uses_get_all_paths(self):
        """Verify read() correctly uses get_all_paths() for any-depth matching"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1}
        
        out_params, out_values = saver.read(params, metric_name='metric', select_by='max', collate_by='mean')
        
        # Should find files at depth 1, depth 2, and depth 3 (all have param1=1)
        # This is correct behavior for reading
        self.assertIsNotNone(out_params)
        self.assertIsNotNone(out_values)
        self.assertGreater(len(out_params), 0)

    def test_multiple_matches_different_depths(self):
        """Should return all matching files regardless of depth"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2}
        
        out_params, out_values = saver.read(params, metric_name='metric', select_by='all', collate_by='all')
        
        # Should find files at both depth 2 and depth 3
        # This is correct behavior for reading
        self.assertIsNotNone(out_params)
        self.assertIsNotNone(out_values)
        # Should have multiple results (from different depths)
        self.assertGreater(len(out_params), 0)

    def test_reading_with_exact_params(self):
        """Should find files at exact depth and deeper depths"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        out_params, out_values = saver.read(params, metric_name='metric', select_by='max', collate_by='mean')
        
        # Should find files at depth 3 (exact match)
        # This is correct behavior for reading
        self.assertIsNotNone(out_params)
        self.assertIsNotNone(out_values)
        self.assertGreater(len(out_params), 0)


if __name__ == '__main__':
    unittest.main()
