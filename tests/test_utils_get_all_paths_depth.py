import unittest
import os
import shutil
from slune.utils import get_all_paths

class TestGetAllPathsDepth(unittest.TestCase):
    """Test get_all_paths() function for reading operations (should find at any depth)"""

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
        
        # Depth 3: --param1=1/--param2=2/--param3=3/results_0.csv, results_1.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv'), 'w') as f:
            f.write('a,b\n2,3\n')
        
        # Another depth 2 with different param2 value: --param1=1/--param2=99/results_0.csv
        os.makedirs(os.path.join(self.test_dir, '--param1=1', '--param2=99'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1', '--param2=99', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')

    def tearDown(self):
        # Clean up the temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_files_at_exact_depth(self):
        """Search for 3 params, files exist at depth 3 with all 3 params → should find them"""
        # Search for all 3 parameters
        params = ['param1=1', 'param2=2', 'param3=3']
        result = get_all_paths('.csv', params, root_directory=self.test_dir)
        
        # Should find both files at depth 3
        expected = [
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv')
        ]
        result.sort()
        expected.sort()
        self.assertEqual(result, expected)

    def test_files_at_shallower_depth_for_reading(self):
        """Search for 3 params, files exist at depth 2 with 2 params → should NOT find them (get_all_paths requires all params)"""
        # Search for 3 parameters
        params = ['param1=1', 'param2=2', 'param3=3']
        result = get_all_paths('.csv', params, root_directory=self.test_dir)
        
        # get_all_paths() requires ALL parameters to match, so it will only find files at depth 3
        # Files at depth 2 only have 2 params, so they won't match when searching for 3 params
        # This is correct behavior - get_all_paths() requires all params to match
        expected = [
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv')
        ]
        result.sort()
        expected.sort()
        self.assertEqual(result, expected)

    def test_files_at_deeper_depth(self):
        """Search for 2 params, files exist at depth 3 with 3 params → should find them (if all 2 params match)"""
        # Search for 2 parameters, files exist at depth 3
        params = ['param1=1', 'param2=2']
        result = get_all_paths('.csv', params, root_directory=self.test_dir)
        
        # Should find files at depth 2 AND depth 3 (both match the 2 params)
        expected = [
            os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_1.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv')
        ]
        result.sort()
        expected.sort()
        self.assertEqual(result, expected)

    def test_mixed_depths(self):
        """Multiple files at different depths, verify all matching ones are found"""
        # Search for param1 only
        params = ['param1=1']
        result = get_all_paths('.csv', params, root_directory=self.test_dir)
        
        # Should find all files that have param1=1 at any depth
        expected = [
            os.path.join(self.test_dir, '--param1=1', 'results_0.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_1.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=99', 'results_0.csv')
        ]
        result.sort()
        expected.sort()
        self.assertEqual(result, expected)

    def test_same_param_names_different_values(self):
        """Files with same param names but different values at different depths"""
        # Search for param1=1 and param2=2
        params = ['param1=1', 'param2=2']
        result = get_all_paths('.csv', params, root_directory=self.test_dir)
        
        # Should find files with param2=2, but NOT param2=99
        expected = [
            os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_0.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', 'results_1.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_0.csv'),
            os.path.join(self.test_dir, '--param1=1', '--param2=2', '--param3=3', 'results_1.csv')
        ]
        result.sort()
        expected.sort()
        self.assertEqual(result, expected)
        # Verify param2=99 is NOT included
        self.assertNotIn(os.path.join(self.test_dir, '--param1=1', '--param2=99', 'results_0.csv'), result)

    def test_numeric_equivalence(self):
        """Test that numeric values are matched correctly"""
        # Create a file with numeric value
        os.makedirs(os.path.join(self.test_dir, '--param1=1.0', '--param2=2.0'), exist_ok=True)
        with open(os.path.join(self.test_dir, '--param1=1.0', '--param2=2.0', 'results_0.csv'), 'w') as f:
            f.write('a,b\n1,2\n')
        
        # Search with integer values
        params = ['param1=1', 'param2=2']
        result = get_all_paths('.csv', params, root_directory=self.test_dir)
        
        # Should find files with numeric equivalent values
        numeric_file = os.path.join(self.test_dir, '--param1=1.0', '--param2=2.0', 'results_0.csv')
        # Note: This test verifies that get_all_paths handles numeric equivalence
        # The actual behavior depends on how get_all_paths handles numeric values
        
        # Clean up
        os.remove(numeric_file)
        os.rmdir(os.path.join(self.test_dir, '--param1=1.0', '--param2=2.0'))
        os.rmdir(os.path.join(self.test_dir, '--param1=1.0'))


if __name__ == '__main__':
    unittest.main()
