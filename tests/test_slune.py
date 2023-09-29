import unittest
from slune.slune import garg

class TestGargFunction(unittest.TestCase):

    def test_single_argument_string(self):
        args_ls = ['--name=John', '--age=25']
        result = garg(args_ls, '--name')
        self.assertEqual(result, 'John')

    def test_single_argument_string_not_found(self):
        args_ls = ['--age=25']
        with self.assertRaises(ValueError):
            garg(args_ls, '--name')

    def test_multiple_arguments_list(self):
        args_ls = ['--name=John', '--age=25', '--city=New York']
        result = garg(args_ls, ['--name', '--age'])
        self.assertEqual(result, ['John', '25'])

    def test_multiple_arguments_list_some_not_found(self):
        args_ls = ['--name=John', '--city=New York']
        with self.assertRaises(ValueError):
            garg(args_ls, ['--name', '--age'])

    def test_invalid_argument_names(self):
        args_ls = ['--name=John', '--age=25']
        with self.assertRaises(TypeError):
            garg(args_ls, 123)

if __name__ == '__main__':
    unittest.main()
