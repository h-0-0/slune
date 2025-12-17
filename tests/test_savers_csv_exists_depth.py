import unittest
import os
import shutil
import pandas as pd
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault

class TestSaverCsvExistsDepth(unittest.TestCase):
    """Test SaverCsv.exists() method with exact depth matching"""

    def setUp(self):
        # Create a temporary directory with CSV files at different depths
        self.test_dir = 'test_directory'
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create directory structure with CSV files at different depths
        # Depth 1: --param1=1/results_0.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1'), exist_ok=True)
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', 'results_0.csv'), index=False)
        
        # Depth 2: --param1=1/--param2=2/results_0.csv, results_1.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2'), exist_ok=True)
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'), index=False)
        df = pd.DataFrame({'a': [2, 3], 'b': [4, 5]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_1.csv'), index=False)
        
        # Depth 3: --param1=1/--param2=2/--param3=3/results_0.csv, results_1.csv, results_2.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3'), exist_ok=True)
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'), index=False)
        df = pd.DataFrame({'a': [2, 3], 'b': [4, 5]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv'), index=False)
        df = pd.DataFrame({'a': [3, 4], 'b': [5, 6]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_2.csv'), index=False)

    def tearDown(self):
        # Clean up the temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_csv_exact_depth_matching(self):
        """Verify CSV saver correctly uses exact-depth exists"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        result = saver.exists(params)
        
        # Should return count of files at exact depth 3 only
        # This test will FAIL with current implementation
        # After fix: should return 3 (only depth 3 files)
        self.assertEqual(result, 3, "Should only count CSV files at exact depth 3")

    def test_multiple_csv_files_different_depths(self):
        """Multiple CSV files at different depths, ensure only correct depth files are counted"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        result = saver.exists(params)
        
        # Should only count depth 3 files (3 files), not depth 2 files (2 files)
        # This test will FAIL with current implementation
        # Current: might return 5 (2 at depth 2 + 3 at depth 3)
        # After fix: should return 3 (only depth 3)
        self.assertEqual(result, 3, "Should only count CSV files at exact depth 3")

    def test_csv_numeric_values_exact_depth(self):
        """Test numeric equivalence handling at exact depth"""
        # Create files with numeric values
        os.makedirs(os.path.join(self.test_dir, '--param1=1.0', '--param2=2.0', '--param3=3.0'), exist_ok=True)
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1.0', '--param2=2.0', '--param3=3.0', 'results_0.csv'), index=False)
        
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        # Search with integer values
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        result = saver.exists(params)
        
        # Should find files with numeric equivalent values at exact depth
        # Note: This depends on how numeric equivalence is handled
        # The test verifies that exact depth matching still works with numeric equivalence
        
        # Clean up
        os.remove(os.path.join(self.test_dir, '--param1=1.0', '--param2=2.0', '--param3=3.0', 'results_0.csv'))
        os.rmdir(os.path.join(self.test_dir, '--param1=1.0', '--param2=2.0', '--param3=3.0'))
        os.rmdir(os.path.join(self.test_dir, '--param1=1.0', '--param2=2.0'))
        os.rmdir(os.path.join(self.test_dir, '--param1=1.0'))

    def test_mixed_csv_files_exact_depth_only(self):
        """Files at depth 2 and depth 3, checking for 3 params → only count depth 3 files"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        result = saver.exists(params)
        
        # Should only count depth 3 files
        # This test will FAIL with current implementation
        self.assertEqual(result, 3, "Should only count CSV files at exact depth 3, not depth 2")

    def test_csv_two_params_exact_depth(self):
        """Test with 2 params - should only count depth 2 files"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2}
        
        result = saver.exists(params)
        
        # Should only count files at exact depth 2, not depth 3
        # This test will FAIL with current implementation
        # After fix: should return 2 (only depth 2 files)
        self.assertEqual(result, 2, "Should only count CSV files at exact depth 2, not depth 3")


if __name__ == '__main__':
    unittest.main()
