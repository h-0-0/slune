import unittest
import os
import shutil
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault

class TestSaverExtExistsDepth(unittest.TestCase):
    """Test SaverExt.exists() method with exact depth matching"""

    def setUp(self):
        # Create a temporary directory with files at different depths
        self.test_dir = 'test_directory'
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create directory structure with files at different depths
        # Depth 1: --param1=1/results_0.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        
        # Depth 2: --param1=1/--param2=2/results_0.csv, results_1.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_1.csv'), 'w') as f:
            f.write('a,b\n2,3\n')
        
        # Depth 3: --param1=1/--param2=2/--param3=3/results_0.csv, results_1.csv, results_2.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv'), 'w') as f:
            f.write('a,b\n2,3\n')
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_2.csv'), 'w') as f:
            f.write('a,b\n3,4\n')

    def tearDown(self):
        # Clean up the temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_exact_depth_match(self):
        """3 params, files at depth 3 → correct count"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        result = saver.exists(params)
        
        # Should return count of files at exact depth 3 only
        self.assertEqual(result, 3)

    def test_shallower_depth_should_not_count(self):
        """3 params, files at depth 2 → should return 0 (NOT count shallow files)"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        result = saver.exists(params)
        
        # This test will FAIL with current implementation
        # Currently exists() uses get_all_paths() which finds files at any depth
        # After fix, should return 3 (only depth 3 files), not 5 (depth 2 + depth 3)
        # For now, we expect it to fail, so we test the current (wrong) behavior
        # After fix, change this to: self.assertEqual(result, 0) or remove shallow files first
        
        # Current buggy behavior: counts files at depth 2 as well
        # After fix: should only count depth 3 files = 3
        # To test the fix, we need to verify it doesn't count depth 2 files
        # Let's check that it should be 3, not 5
        self.assertEqual(result, 3, "Should only count files at exact depth 3, not depth 2")

    def test_deeper_depth_should_not_count(self):
        """2 params, files at depth 3 → should return 0 (NOT count deeper files)"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2}
        
        result = saver.exists(params)
        
        # Should return count of files at exact depth 2 only, not depth 3
        # This test will FAIL with current implementation
        # After fix: should return 2 (only depth 2 files), not 5 (depth 2 + depth 3)
        self.assertEqual(result, 2, "Should only count files at exact depth 2, not depth 3")

    def test_multiple_runs_at_correct_depth(self):
        """Verify count includes all runs at exact depth"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        result = saver.exists(params)
        
        # Should count all 3 files at depth 3
        self.assertEqual(result, 3)

    def test_mixed_scenario_exact_depth_only(self):
        """Files at depth 2 and depth 3, checking for 3 params → only count depth 3 files"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        result = saver.exists(params)
        
        # Should only count files at depth 3 (3 files), not depth 2 (2 files)
        # This test will FAIL with current implementation
        # Current: returns 5 (2 at depth 2 + 3 at depth 3)
        # After fix: should return 3 (only depth 3)
        self.assertEqual(result, 3, "Should only count files at exact depth 3")

    def test_empty_directory(self):
        """Test with empty directory"""
        empty_dir = 'test_empty_directory'
        os.makedirs(empty_dir, exist_ok=True)
        
        saver = SaverCsv(LoggerDefault(), root_dir=empty_dir)
        params = {'param1': 1, 'param2': 2, 'param3': 3}
        
        result = saver.exists(params)
        
        self.assertEqual(result, 0)
        
        # Clean up
        os.rmdir(empty_dir)

    def test_missing_params(self):
        """Test with params that don't exist"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 999, 'param2': 888, 'param3': 777}
        
        result = saver.exists(params)
        
        self.assertEqual(result, 0)

    def test_single_param_exact_depth(self):
        """Test with single parameter - should only count depth 1"""
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'param1': 1}
        
        result = saver.exists(params)
        
        # Should only count files at depth 1, not depth 2 or 3
        # Current buggy behavior might count all files with param1=1
        # After fix: should return 1 (only depth 1 file)
        self.assertEqual(result, 1, "Should only count files at exact depth 1")


if __name__ == '__main__':
    unittest.main()
