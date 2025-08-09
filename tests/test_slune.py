import unittest
from unittest.mock import patch, call, MagicMock
from slune import submit_job, sbatchit
import os

class TestSubmitJob(unittest.TestCase):
    @patch('subprocess.run')
    def test_regular(self, mock_run):
        # Arrange
        sh_path = os.path.join('path','to','bash','script')
        args = {"arg1": 1, "arg2": "two", "arg3": False}

        # Act
        submit_job(sh_path, args=args)

        # Assert
        mock_run.assert_called_once_with(['sbatch', sh_path, '--arg1=1', '--arg2=two', '--arg3=False'], check=True)

class TestSbatchit(unittest.TestCase):
    @patch('subprocess.run')
    def test_sbatchit(self, mock_run):
        # Arrange
        script_path = os.path.join('path','to','script')
        template_path = os.path.join('path','to','template')
        searcher = MagicMock()
        searcher.__iter__.return_value = [{'arg1':1, 'arg2':'two'}, {'arg3':False, 'arg4':0.5}]
        cargs = {"carg1":"str", "carg2":"str"}
        saver = None

        # Act
        sbatchit(script_path, template_path, searcher, cargs, saver)

        # Assert
        calls = [call(['sbatch', template_path, script_path, '--carg1=str', '--carg2=str', '--arg1=1', '--arg2=two'], check=True),
                 call(['sbatch', template_path, script_path, '--carg1=str', '--carg2=str', '--arg3=False', '--arg4=0.5'], check=True)]
        mock_run.assert_has_calls(calls, any_order=True)


if __name__ == '__main__':
    unittest.main()
