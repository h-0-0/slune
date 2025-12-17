import unittest
import os
import shutil
import pandas as pd
from slune.searchers.grid import SearcherGrid
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault

class TestIntegrationGridCsvDepth(unittest.TestCase):
    """Integration test: SearcherGrid + SaverCsv with depth issues"""

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

    def test_previous_runs_2_params_new_search_3_params(self):
        """Previous runs saved with 2 params, new search with 3 params → should run all configs"""
        # First, save some runs with 2 params
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        saver1 = SaverCsv(logger1, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Now create a searcher with 3 params
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        saver2 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver2)
        
        # Should not skip - the 2-param files should not count for 3-param search
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 3})

    def test_some_configs_depth_2_some_depth_3(self):
        """Some configs have files at depth 2, some at depth 3 → verify correct behavior for each"""
        # Create files at depth 2 for param1=1, param2=2
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        saver1 = SaverCsv(logger1, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Create files at depth 3 for param1=1, param2=2, param3=3 (2 runs so it will skip)
        logger2 = LoggerDefault()
        logger2.log({'metric': 0.6})
        saver2 = SaverCsv(logger2, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        saver2.save_collated()
        logger3 = LoggerDefault()
        logger3.log({'metric': 0.7})
        saver3 = SaverCsv(logger3, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        saver3.save_collated()
        
        # Create searcher with mixed configs
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3, 4]  # Two values for param3
        }, runs=2)
        
        saver4 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver4)
        
        # First config (param3=3) should skip (has 2 runs at exact depth, enough)
        # Second config (param3=4) should not skip (no exact depth files)
        config = searcher.next_tune()
        # Should skip config with param3=3 and return param3=4
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 4})

    def test_incremental_parameter_addition(self):
        """Incremental parameter addition: Start with 1 param, add 2nd, add 3rd → verify existing runs counted correctly at each stage"""
        # Stage 1: Save with 1 param
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        saver1 = SaverCsv(logger1, params={'param1': 1}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Stage 2: Search with 2 params
        searcher2 = SearcherGrid({
            "--param1": [1],
            "--param2": [2]
        }, runs=2)
        
        saver2 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher2.check_existing_runs(saver2)
        
        # Should not skip - 1-param files should not count for 2-param search
        config = searcher2.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2})
        
        # Save with 2 params
        logger3 = LoggerDefault()
        logger3.log({'metric': 0.6})
        saver3 = SaverCsv(logger3, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver3.save_collated()
        
        # Stage 3: Search with 3 params
        searcher3 = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        saver4 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher3.check_existing_runs(saver4)
        
        # Should not skip - 2-param files should not count for 3-param search
        # This test will FAIL with current implementation
        config = searcher3.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 3})

    def test_full_workflow_check_existing_iterate(self):
        """Full workflow: Create searcher, check existing runs, iterate through configs → verify correct skipping"""
        # Create some existing files at depth 2
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        saver1 = SaverCsv(logger1, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Create searcher with 3 params
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        saver2 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver2)
        
        # Should iterate through configs correctly
        configs = []
        try:
            for i in range(10):  # Limit iterations
                configs.append(searcher.next_tune())
        except IndexError:
            pass  # Expected when grid is exhausted
        
        # Should have gotten the config (not skipped due to shallow files)
        self.assertGreater(len(configs), 0)
        self.assertEqual(configs[0], {"--param1": 1, "--param2": 2, "--param3": 3})

    def test_mixed_depths_in_grid(self):
        """Multiple configs with different param counts, files at various depths → verify correct skipping behavior"""
        # Create files at different depths
        # Depth 2: param1=1, param2=2
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        saver1 = SaverCsv(logger1, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Depth 3: param1=1, param2=2, param3=3 (2 runs)
        logger2 = LoggerDefault()
        logger2.log({'metric': 0.6})
        saver2 = SaverCsv(logger2, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        saver2.save_collated()
        logger3 = LoggerDefault()
        logger3.log({'metric': 0.7})
        saver3 = SaverCsv(logger3, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        saver3.save_collated()
        
        # Create searcher
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3, 4]
        }, runs=2)
        
        saver4 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver4)
        
        # Config with param3=3 should skip (has 2 runs at exact depth)
        # Config with param3=4 should not skip (no exact depth files)
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 4})

    def test_actual_csv_files_real_directory(self):
        """Test with actual CSV files: Create real directory structure, use real SaverCsv, verify behavior"""
        # Create real files at depth 2
        logger1 = LoggerDefault()
        logger1.log({'metric': 0.5})
        logger1.log({'metric': 0.6})
        saver1 = SaverCsv(logger1, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver1.save_collated()
        
        # Verify file exists (check both path formats)
        expected_file1 = os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv')
        expected_file2 = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'results_0.csv')
        self.assertTrue(os.path.exists(expected_file1) or os.path.exists(expected_file2), 
                       f"File should exist at {expected_file1} or {expected_file2}")
        
        # Create searcher with 3 params
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        saver2 = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver2)
        
        # Should not skip based on depth 2 files
        # The searcher has only 1 config, so it should return it (not skip)
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 3})
        
        # Verify that exists() returns 0 for 3 params (no exact depth files)
        count = saver2.exists({'param1': 1, 'param2': 2, 'param3': 3})
        self.assertEqual(count, 0, "Should return 0 since no files exist at exact depth 3")


if __name__ == '__main__':
    unittest.main()
