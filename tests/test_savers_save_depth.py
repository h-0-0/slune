import unittest
import os
import pandas as pd
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault

class TestSaverSaveDepth(unittest.TestCase):
    """Test SaverExt.get_path() and saving methods - should save at full depth"""

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = 'test_directory'
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
        
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        # Clean up the temporary directory
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    def test_get_path_with_3_params(self):
        """get_path() with 3 params: Should return path at depth 3 with all 3 params"""
        logger = LoggerDefault()
        saver = SaverCsv(logger, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        
        path = saver.current_path
        
        # Should create path at depth 3
        # Note: get_path() creates paths without '--' prefix when params don't have '--'
        expected_path = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'param3=3', 'results_0.csv')
        self.assertEqual(path, expected_path)

    def test_get_path_with_2_params(self):
        """get_path() with 2 params: Should return path at depth 2 with all 2 params"""
        logger = LoggerDefault()
        saver = SaverCsv(logger, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        
        path = saver.current_path
        
        # Should create path at depth 2
        # Note: get_path() creates paths without '--' prefix when params don't have '--'
        expected_path = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'results_0.csv')
        self.assertEqual(path, expected_path)

    def test_save_with_3_params(self):
        """Save with 3 params: Should create directory structure at depth 3 with all 3 params"""
        logger = LoggerDefault()
        logger.log({'metric': 0.5})
        logger.log({'metric': 0.6})
        
        saver = SaverCsv(logger, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        saver.save_collated()
        
        # Verify file was created at depth 3
        # Note: paths are created without '--' prefix
        expected_file = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'param3=3', 'results_0.csv')
        self.assertTrue(os.path.exists(expected_file))
        
        # Verify directory structure was created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'param1=1')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'param1=1', 'param2=2')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'param1=1', 'param2=2', 'param3=3')))

    def test_save_with_2_params(self):
        """Save with 2 params: Should create directory structure at depth 2 with all 2 params"""
        logger = LoggerDefault()
        logger.log({'metric': 0.5})
        logger.log({'metric': 0.6})
        
        saver = SaverCsv(logger, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver.save_collated()
        
        # Verify file was created at depth 2
        # Note: paths are created without '--' prefix
        expected_file = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'results_0.csv')
        self.assertTrue(os.path.exists(expected_file))
        
        # Verify directory structure was created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'param1=1')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'param1=1', 'param2=2')))

    def test_get_path_determines_full_depth(self):
        """Verify get_path() correctly determines full depth path"""
        logger = LoggerDefault()
        saver = SaverCsv(logger, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        
        # Get path using get_path method directly
        from slune.utils import dict_to_strings
        path = saver.get_path(dict_to_strings({'param1': 1, 'param2': 2, 'param3': 3}))
        
        # Should be at depth 3
        # Note: get_path() creates paths without '--' prefix when params don't have '--'
        expected_path = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'param3=3', 'results_0.csv')
        self.assertEqual(path, expected_path)

    def test_files_saved_correct_location(self):
        """Verify files are saved in correct location matching all parameters"""
        logger = LoggerDefault()
        logger.log({'metric': 0.5})
        
        saver = SaverCsv(logger, params={'param1': 1, 'param2': 2, 'param3': 3}, root_dir=self.test_dir)
        saver.save_collated()
        
        # Verify file exists at correct location
        # Note: paths are created without '--' prefix
        expected_file = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'param3=3', 'results_0.csv')
        self.assertTrue(os.path.exists(expected_file))
        
        # Verify file content
        df = pd.read_csv(expected_file)
        self.assertIn('metric', df.columns)

    def test_save_collated_creates_files_at_correct_depth(self):
        """Test save_collated() creates files at correct depth"""
        logger = LoggerDefault()
        logger.log({'metric': 0.5})
        logger.log({'metric': 0.6})
        
        saver = SaverCsv(logger, params={'param1': 1, 'param2': 2}, root_dir=self.test_dir)
        saver.save_collated()
        
        # Verify file was created at depth 2 (not depth 1 or 3)
        # Note: paths are created without '--' prefix
        expected_file = os.path.join(self.test_dir, 'param1=1', 'param2=2', 'results_0.csv')
        self.assertTrue(os.path.exists(expected_file))
        
        # Verify no file was created at depth 1
        depth1_file = os.path.join(self.test_dir, 'param1=1', 'results_0.csv')
        self.assertFalse(os.path.exists(depth1_file))


if __name__ == '__main__':
    unittest.main()
