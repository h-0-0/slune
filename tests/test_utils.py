import unittest
import os
from slune.utils import find_directory_path, dict_to_strings

class TestFindDirectoryPath(unittest.TestCase):

    def setUp(self):
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


class TestDictToStrings(unittest.TestCase):

    def test_dict_to_strings(self):
        d = {'arg1': 1, 'arg2': 2}
        result = dict_to_strings(d)
        self.assertEqual(result, ['--arg1=1', '--arg2=2'])
    