import unittest
from unittest.mock import patch, call, MagicMock
from slune import garg, submit_job, sbatchit

class TestSubmitJob(unittest.TestCase):
    @patch('subprocess.run')
    def test_regular(self, mock_run):
        # Arrange
        sh_path = "/path/to/bash/script"
        args = ["arg1", "arg2"]

        # Act
        submit_job(sh_path, args)

        # Assert
        mock_run.assert_called_once_with(['sbatch', sh_path, 'arg1', 'arg2'], check=True)

class TestSbatchit(unittest.TestCase):
    @patch('subprocess.run')
    def test_sbatchit(self, mock_run):
        # Arrange
        script_path = "/path/to/script"
        template_path = "/path/to/template"
        searcher = MagicMock()
        searcher.__iter__.return_value = [['arg1', 'arg2'], ['arg3', 'arg4']]
        cargs = ["carg1", "carg2"]
        slog = None

        # Act
        sbatchit(script_path, template_path, searcher, cargs, slog)

        # Assert
        calls = [call(['sbatch', template_path, script_path, 'carg1', 'carg2', 'arg1', 'arg2'], check=True),
                 call(['sbatch', template_path, script_path, 'carg1', 'carg2', 'arg3', 'arg4'], check=True)]
        mock_run.assert_has_calls(calls, any_order=True)

class TestGarg(unittest.TestCase):

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
