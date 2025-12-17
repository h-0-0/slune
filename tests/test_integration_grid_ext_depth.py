import unittest
import os
import shutil
import pandas as pd
from slune.searchers.grid import SearcherGrid
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault

class TestIntegrationGridExtDepth(unittest.TestCase):
    """Integration test: SearcherGrid + SaverExt with depth issues"""

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

    def test_grid_with_base_saver_ext(self):
        """Similar to Grid+CSV tests but with SaverExt base class"""
        # Create files at depth 2
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        
        # Create searcher with 3 params
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver)
        
        # Should not skip based on depth 2 files
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 3})

    def test_different_file_extensions(self):
        """Test with different file extensions (.csv, .json, etc.)"""
        # Create files with .csv extension at depth 2
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2'), exist_ok=True)
        import pandas as pd
        df = pd.DataFrame({'a': [1], 'b': [2]})
        df.to_csv(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'), index=False)
        
        # Create searcher with 3 params
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3]
        }, runs=2)
        
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver)
        
        # Should not skip based on depth 2 files
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 3})

    def test_verify_base_class_behavior(self):
        """Verify base class behavior is correct"""
        # Create files at depth 2 and depth 3
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv'), 'w') as f:
            f.write('a,b\n2,3\n')
        
        # Test exists() with 3 params - should only count depth 3
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        count = saver.exists({'param1': 1, 'param2': 2, 'param3': 3})
        
        # Should only count depth 3 files (2 files), not depth 2
        self.assertEqual(count, 2, "Should only count files at exact depth 3")
        
        # Test exists() with 2 params - should only count depth 2
        count = saver.exists({'param1': 1, 'param2': 2})
        
        # Should only count depth 2 files (1 file), not depth 3
        self.assertEqual(count, 1, "Should only count files at exact depth 2")

    def test_searcher_with_base_saver_mixed_depths(self):
        """Test searcher with base saver and mixed depth scenarios"""
        # Create files at different depths
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv'), 'w') as f:
            f.write('a,b\n2,3\n')
        
        # Create searcher
        searcher = SearcherGrid({
            "--param1": [1],
            "--param2": [2],
            "--param3": [3, 4]
        }, runs=2)
        
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        searcher.check_existing_runs(saver)
        
        # Config with param3=3 should skip (has 2 runs at exact depth)
        # Config with param3=4 should not skip (no exact depth files)
        config = searcher.next_tune()
        self.assertEqual(config, {"--param1": 1, "--param2": 2, "--param3": 4})


if __name__ == '__main__':
    unittest.main()
