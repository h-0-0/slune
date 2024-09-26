import unittest
import os
from slune.utils import find_directory_path, dict_to_strings, strings_to_dict, find_ext_files, get_all_paths, get_numeric_equiv

class TestFindDirectoryPath(unittest.TestCase):

    def setUp(self):
        # Delete the test directory and all contents if it already exists
        if os.path.exists('test_directory'):
            for root, dirs, files in os.walk('test_directory', topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        # Create a temporary directory structure for testing
        self.test_dir = 'test_directory'
        os.makedirs(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder3=0.3'))
        os.makedirs(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.22', '--folder3=0.33', '--folder4=0.4'))
        os.makedirs(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', 'another_folder'))
        os.makedirs(os.path.join(self.test_dir, '--folder1=0.1', '--folder5=0.5', '--folder6=0.6'))

    def tearDown(self):
        # Clean up the temporary directory structure
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder3=0.3'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.22', '--folder3=0.33', '--folder4=0.4'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.22', '--folder3=0.33'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', 'another_folder'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.22'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder5=0.5', '--folder6=0.6'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder5=0.5'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1'))
        os.rmdir(self.test_dir)

    def test_matching_path(self):
        search_strings = ['--folder1=', '--folder2=', '--folder3=']
        result = find_directory_path(search_strings, root_directory=self.test_dir)
        self.assertEqual(result, os.path.join(self.test_dir, '--folder1=', '--folder2=', '--folder3='))
    
    def test_matching_path_diff_order(self):
        search_strings = ['--folder2=', '--folder3=', '--folder1=']
        result = find_directory_path(search_strings, root_directory=self.test_dir)
        self.assertEqual(result, os.path.join(self.test_dir, '--folder1=', '--folder2=', '--folder3='))

    def test_partial_match(self):
        search_strings = ['--folder1=', '--folder2=', '--missing_folder=']
        result = find_directory_path(search_strings, root_directory=self.test_dir)
        self.assertEqual(result, os.path.join(self.test_dir, '--folder1=', '--folder2='))

    def test_partial_match_diff_order(self):
        search_strings = ['--folder2=', '--missing_folder=', '--folder1=']
        result = find_directory_path(search_strings, root_directory=self.test_dir)
        self.assertEqual(result, os.path.join(self.test_dir, '--folder1=', '--folder2='))

    def test_no_match(self):
        search_strings = ['--nonexistent_folder1=', '--nonexistent_folder2=']
        result = find_directory_path(search_strings, root_directory=self.test_dir)
        self.assertEqual(result, self.test_dir)

    def test_deepest(self):
        search_strings = ['--folder1=', '--folder2=', '--folder3=', '--folder4=']
        result = find_directory_path(search_strings, root_directory=self.test_dir)
        self.assertEqual(result, os.path.join(self.test_dir, '--folder1=', '--folder2=', '--folder3=', '--folder4='))
    
    def test_root_dir_with_forward_slash(self):
        search_strings = ['--folder2=', '--folder3=']
        result = find_directory_path(search_strings, root_directory= os.path.join(self.test_dir,'--folder1=0.1'))
        self.assertEqual(result, os.path.join(self.test_dir,'--folder1=0.1', '--folder2=', '--folder3='))

    def test_just_root_dir_forward_slash(self):
        search_strings = ['--folder_not_there=']
        result = find_directory_path(search_strings, root_directory= os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', 'another_folder'))
        self.assertEqual(result, os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', 'another_folder'))

    def test_existing_duplicate_dirs(self):
        os.makedirs(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder2=2.2'))
        search_strings = ['--folder1=', '--folder2=']
        result = find_directory_path(search_strings, root_directory=self.test_dir)
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder2=2.2'))
        self.assertEqual(result, os.path.join(self.test_dir, '--folder1=', '--folder2='))

class TestNumericEquiv(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_directory'
        os.makedirs(os.path.join(self.test_dir, '--dir1=1', '--dir2=2', '--dir3=3'))
    
    def tearDown(self):
        os.rmdir(os.path.join(self.test_dir, '--dir1=1', '--dir2=2', '--dir3=3'))
        os.rmdir(os.path.join(self.test_dir, '--dir1=1', '--dir2=2'))
        os.rmdir(os.path.join(self.test_dir, '--dir1=1'))
        os.rmdir(self.test_dir)

    def test_get_numeric_equiv_full_path_exist(self):
        path = os.path.join('--dir1=1','--dir2=2')
        expected = os.path.join(self.test_dir, '--dir1=1', '--dir2=2')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)

    def test_get_numeric_equiv_path_longer_than_existing(self):
        path = os.path.join('--dir1=1','--dir2=2','--dir4=4')
        expected = os.path.join(self.test_dir, '--dir1=1', '--dir2=2', '--dir4=4')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)

    def test_get_numeric_equiv_full_path_exist_diff_numeric_value(self):
        path = os.path.join('--dir1=1','--dir2=2.00')
        expected = os.path.join(self.test_dir, '--dir1=1', '--dir2=2')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)

    def test_get_numeric_equiv_none_of_path_exist(self):
        path = os.path.join('--dir5=5','--dir6=6')
        expected =  os.path.join(self.test_dir, '--dir5=5', '--dir6=6')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)

    def test_get_numeric_equiv_numeric_equiv_exist_then_none(self):
        path = os.path.join('--dir1=1.0','--dir4=4')
        expected = os.path.join(self.test_dir, '--dir1=1', '--dir4=4')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)
    
    def test_get_numeric_equiv_exists_then_numeric_equiv(self):
        path = os.path.join('--dir1=1','--dir2=2.0')
        expected = os.path.join(self.test_dir, '--dir1=1', '--dir2=2')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)

        path = os.path.join('--dir1=1','--dir2=2.0','--dir3=3')
        expected = os.path.join(self.test_dir, '--dir1=1', '--dir2=2', '--dir3=3')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)
    
    def test_get_numerc_equiv_numeric_equiv_then_exists(self):
        path = os.path.join('--dir1=1.0','--dir2=2')
        expected = os.path.join(self.test_dir, '--dir1=1', '--dir2=2')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)

        path = os.path.join('--dir1=1.0','--dir2=2','--dir3=3')
        expected = os.path.join(self.test_dir, '--dir1=1', '--dir2=2', '--dir3=3')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)

    def test_get_numeric_directory_with_no_equals(self):
        os.makedirs(os.path.join(self.test_dir, '--dir1=1', '--dir2=2', '--dir_no_equals'))

        path = os.path.join('--dir1=1.0','--dir2=2', '--dir_no_equals')
        expected = os.path.join(self.test_dir, '--dir1=1', '--dir2=2', '--dir_no_equals')
        self.assertEqual(get_numeric_equiv(path, self.test_dir), expected)   

        os.rmdir(os.path.join(self.test_dir, '--dir1=1', '--dir2=2', '--dir_no_equals'))


class TestDictToStrings(unittest.TestCase):

    def test_common(self):
        d = {'arg1': 1, 'arg2': 2}
        result = dict_to_strings(d)
        self.assertEqual(result, ['arg1=1', 'arg2=2'])

    def test_value_none(self):
        d = {'arg1': None, 'arg2': 2}
        result = dict_to_strings(d)
        self.assertEqual(result, ['arg1', 'arg2=2'])
    
    def test_double_dash(self):
        d = {'--arg1': 1, '--arg2': 2}
        result = dict_to_strings(d)
        self.assertEqual(result, ['--arg1=1', '--arg2=2'])
    
    def test_double_dash_value_none(self):
        d = {'--arg1': None, '--arg2': 2}
        result = dict_to_strings(d)
        self.assertEqual(result, ['--arg1', '--arg2=2'])

    def test_mixed(self):
        d = {'arg1': 1, '--arg2': 2}
        result = dict_to_strings(d)
        self.assertEqual(result, ['arg1=1', '--arg2=2'])

    def test_key_has_equal(self):
        d = {'arg1=': 1, 'arg2=': 2}
        # Check if the function raises a ValueError
        with self.assertRaises(ValueError):
            dict_to_strings(d)
        
    def test_value_has_equal(self):
        d = {'arg1': '1=', 'arg2': '2='}
        # Check if the function raises a ValueError
        with self.assertRaises(ValueError):
            dict_to_strings(d)

class TestStringsToDict(unittest.TestCase):

    def test_common(self):
        s = ['arg1=1', 'arg2=2']
        result = strings_to_dict(s)
        self.assertEqual(result, {'arg1': 1, 'arg2': 2})

    def test_double_dash(self):
        s = ['-arg1=1', '-arg2=2']
        result = strings_to_dict(s)
        self.assertEqual(result, {'arg1': 1, 'arg2': 2})

    def test_double_dash(self):
        s = ['--arg1=1', '--arg2=2']
        result = strings_to_dict(s)
        self.assertEqual(result, {'arg1': 1, 'arg2': 2})

    def test_mixed(self):
        s = ['arg1=1', '--arg2=2']
        result = strings_to_dict(s)
        self.assertEqual(result, {'arg1': 1, 'arg2': 2})

    def test_key_has_double_equals(self):
        s = ['arg1==1', 'arg2=2']
        # Check if the function raises a ValueError
        with self.assertRaises(ValueError):
            strings_to_dict(s)

    def test_value_has_equals(self):
        s = ['arg1=1=', 'arg2=2']
        with self.assertRaises(ValueError):
            strings_to_dict(s)

class TestFindCSVFiles(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory with some CSV files for testing
        self.test_dir = 'test_directory'
        os.makedirs(self.test_dir, exist_ok=True)

        # Creating some CSV files
        self.csv_files = [
            'file1.csv',
            'file2.csv',
            os.path.join('subdir1','file3.csv'),
            os.path.join('subdir2','file4.csv'),
            os.path.join('subdir2','subdir3','file5.csv')
        ]

        for file in self.csv_files:
            file_path = os.path.join(self.test_dir, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write("Sample CSV content")

    def tearDown(self):
        # Clean up the temporary directory and files after testing
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_find_ext_files(self):
        # Test the find_ext_files function

        # Call the function to get the result
        result = find_ext_files('.csv',self.test_dir)

        # Define the expected result based on the files we created
        expected_result = [
            os.path.join(self.test_dir, file) for file in self.csv_files
        ]

        # Sort both lists for comparison, as the order might not be guaranteed
        result.sort()
        expected_result.sort()

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)


class TestGetAllPaths(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory with some CSV files for testing
        self.test_dir = 'test_directory'
        os.makedirs(self.test_dir, exist_ok=True)

        # Creating some CSV files with specific subdirectory paths
        self.csv_files = [
            os.path.join('dir1','file1.csv'),
            os.path.join('dir2','file2.csv'),
            os.path.join('dir1','--subdir=1','file3.csv'),
            os.path.join('dir2','--subdir=2','file4.csv'),
            os.path.join('dir2','--subdir=2','--subdir=3','file5.csv')
        ]

        for file in self.csv_files:
            file_path = os.path.join(self.test_dir, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write("Sample CSV content")

    def tearDown(self):
        # Clean up the temporary directory and files after testing
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_one_match(self):
        # Call the function to get the result
        result = get_all_paths('.csv', ['dir1', '--subdir=1'], self.test_dir)

        # Define the expected result based on the files we created
        expected_result = [
            os.path.join(self.test_dir, 'dir1','--subdir=1','file3.csv')
        ]

        # Sort both lists for comparison, as the order might not be guaranteed
        result.sort()
        expected_result.sort()

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)
    
    def test_multi_match(self):
        # Call the function to get the result
        result = get_all_paths('.csv', ['dir2', '--subdir=2'], self.test_dir)

        # Define the expected result based on the files we created
        expected_result = [
            os.path.join(self.test_dir, 'dir2','--subdir=2','file4.csv'),
            os.path.join(self.test_dir, 'dir2','--subdir=2','--subdir=3','file5.csv')
        ]

        # Sort both lists for comparison, as the order might not be guaranteed
        result.sort()
        expected_result.sort()

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)
    
    def test_depth(self):
        # Call the function to get the result
        result = get_all_paths('.csv', ['dir1'], self.test_dir)

        # Define the expected result based on the files we created
        expected_result = [
            os.path.join(self.test_dir, 'dir1','file1.csv'),
            os.path.join(self.test_dir, 'dir1','--subdir=1','file3.csv')
        ]

        # Sort both lists for comparison, as the order might not be guaranteed
        result.sort()
        expected_result.sort()

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_no_match(self):
        # Call the function to get the result
        result = get_all_paths('.csv', ['dir3'], self.test_dir)

        # Define the expected result based on the files we created
        expected_result = []

        # Sort both lists for comparison, as the order might not be guaranteed
        result.sort()
        expected_result.sort()

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_params_deep(self):
        # Call the function to get the result
        result = get_all_paths('.csv', ['--subdir=3'], self.test_dir)

        # Define the expected result based on the files we created
        expected_result = [
            os.path.join(self.test_dir, 'dir2','--subdir=2','--subdir=3','file5.csv')
        ]

        # Sort both lists for comparison, as the order might not be guaranteed
        result.sort()
        expected_result.sort()

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)
    
    def test_root_has_forwardslash(self):
        # Call the function to get the result
        result = get_all_paths('.csv', ['--subdir=1'], os.path.join(self.test_dir, 'dir1'))

        # Define the expected result based on the files we created
        expected_result = [
            os.path.join(self.test_dir, 'dir1','--subdir=1','file3.csv')
        ]

        # Sort both lists for comparison, as the order might not be guaranteed
        result.sort()
        expected_result.sort()

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_numerically_equiv(self):
        # Call the function to get the result
        result = get_all_paths('.csv', ['--subdir=2.0'], self.test_dir)

        # Define the expected result based on the files we created
        expected_result = [
            os.path.join(self.test_dir, 'dir2','--subdir=2','file4.csv'),
            os.path.join(self.test_dir, 'dir2','--subdir=2','--subdir=3','file5.csv')
        ]

        # Sort both lists for comparison, as the order might not be guaranteed
        result.sort()
        expected_result.sort()

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_numerically_equiv_multi(self):
        # Call the function to get the result
        result = get_all_paths('.csv', ['--subdir=2.00', '--subdir=3e0'], self.test_dir)

        # Define the expected result based on the files we created
        expected_result = [
            os.path.join(self.test_dir, 'dir2','--subdir=2','--subdir=3','file5.csv')
        ]

        # Sort both lists for comparison, as the order might not be guaranteed
        result.sort()
        expected_result.sort()

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()