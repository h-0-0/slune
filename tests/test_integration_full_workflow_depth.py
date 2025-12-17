import unittest
import os
import shutil
import pandas as pd
from slune.searchers.grid import SearcherGrid
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault

class TestIntegrationFullWorkflowDepth(unittest.TestCase):
    """Integration test: Complete workflow from search to save to check"""

    def setUp(self):
        # Create a temporary directory
        self.test_dir = 'test_directory'
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        # Clean up the temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_complete_cycle_save_2_params_search_3_params(self):
        """Complete cycle: Save runs with 2 params → Search with 3 params → Check existing → Verify behavior"""
        # Step 1: Save runs with 2 params
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        logger1.log({'metric': 0.6})
        saver1 = SaverCsv(logger1, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Verify file was created (check both path formats)
        expected_file1 = os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv')
        expected_file2 = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'results_0.csv')
        self.assertTrue(os.path.exists(expected_file1) or os.path.exists(expected_file2),
                       f"File should exist at {expected_file1} or {expected_file2}")
        
        # Step 2: Search with 3 params
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        saver2 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver2)
        
        # Step 3: Check existing and verify behavior
        # Should not skip - 2-param files should not count for 3-param search
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 3})

    def test_multiple_cycles_increasing_parameter_counts(self):
        """Multiple cycles: Run multiple searches with increasing parameter counts"""
        # Cycle 1: Save with 1 param, search with 2 params
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        saver1 = SaverCsv(logger1, params={'param1': 1}, root_dir=self.test_dir)
        saver1.save_collated()
        
        searcher1 = SearcherGrid({
            "--param1": [1],
            "--param2": [2]
        }, runs=2)
        
        saver2 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher1.check_existing_runs(saver2)
        
        # Should not skip
        config = searcher1.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2})
        
        # Cycle 2: Save with 2 params, search with 3 params
        logger2 = LoggerDefault()
        logger2.log({'metric': 0.6})
        saver3 = SaverCsv(logger2, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver3.save_collated()
        
        searcher2 = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        saver4 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher2.check_existing_runs(saver4)
        
        # Should not skip - 2-param files should not count for 3-param search
        # This test will FAIL with current implementation
        config = searcher2.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 3})

    def test_real_file_system_actual_directory_structure(self):
        """Real file system: Use actual directory structure, create and read real files"""
        # Create real files at depth 2
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        logger1.log({'metric': 0.6})
        saver1 = SaverCsv(logger1, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Verify file exists and can be read (check both path formats)
        expected_file1 = os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv')
        expected_file2 = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'results_0.csv')
        expected_file = expected_file1 if os.path.exists(expected_file1) else expected_file2
        self.assertTrue(os.path.exists(expected_file), f"File should exist at {expected_file1} or {expected_file2}")
        df = pd.read_csv(expected_file)
        self.assertIn('metric', df.columns)
        
        # Create searcher with 3 params
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        saver2 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver2)
        
        # Should not skip based on depth 2 files
        # This test will FAIL with current implementation
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 3})

    def test_with_logger_default_in_workflow(self):
        """Test with LoggerDefault: Include logger in the workflow"""
        # Create logger and save
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        logger1.log({'metric': 0.6})
        saver1 = SaverCsv(logger1, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Create searcher
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        # Create new logger and saver for search
        logger2 = LoggerDefault()
        saver2 = SaverCsv(logger2, root_dir=self.test_dir)
        searcher.check_existing_runs(saver2)
        
        # Should not skip
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 3})
        
        # Use the config to log and save
        logger2.log({'metric': 0.7})
        # Create a new saver with the params to save
        saver3 = SaverCsv(logger2, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        saver3.save_collated()
        
        # Verify file was created at correct depth
        # Note: get_path() creates paths without '--' prefix when params don't have '--'
        # Check both formats
        depth3_dir_with_dash = os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3')
        depth3_dir_without_dash = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'param3=3')
        depth3_dir = depth3_dir_with_dash if os.path.exists(depth3_dir_with_dash) else depth3_dir_without_dash
        self.assertTrue(os.path.exists(depth3_dir), f"Directory should exist at depth 3: {depth3_dir_with_dash} or {depth3_dir_without_dash}")
        files = [f for f in os.listdir(depth3_dir) if f.endswith('.csv')]
        self.assertGreater(len(files), 0, "Should have at least one CSV file at depth 3")

    def test_full_workflow_save_check_read(self):
        """Complete workflow: Save → Check existing → Read results"""
        # Step 1: Save with 2 params
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        saver1 = SaverCsv(logger1, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Step 2: Save with 3 params
        logger2 = LoggerDefault()
        logger2.log({'metric': 0.6})
        saver2 = SaverCsv(logger2, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        saver2.save_collated()
        
        # Step 3: Check existing with 3 params
        saver3 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        count = saver3.exists({'param1': 1, 'param2': 2, 'param3': 3})
        
        # Should only count depth 3 files (1 file), not depth 2
        # This test will FAIL with current implementation
        self.assertEqual(count, 1, "Should only count files at exact depth 3")
        
        # Step 4: Read with 2 params (should find both depth 2 and depth 3)
        out_params, out_values = saver3.read({'param1': 1, 'param2': 2}, metric_name='metric', select_by='max', collate_by='mean')
        
        # Should find files at both depths (correct behavior for reading)
        self.assertIsNotNone(out_params)
        self.assertIsNotNone(out_values)
        self.assertGreater(len(out_params), 0)


if __name__ == '__main__':
    unittest.main()
