import unittest
from unittest.mock import patch, call, MagicMock
from slune import submit_job, sbatchit
from slune.searchers.grid import SearcherGrid
from slune.slune import get_csv_saver
from slune.loggers.default import LoggerDefault
from slune.savers.csv import SaverCsv
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


class TestEndToEndWorkflow(unittest.TestCase):
    def setUp(self):
        self.tmp_root = os.path.join("test_directory_int")
        if os.path.isdir(self.tmp_root):
            for root, dirs, files in os.walk(self.tmp_root, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.tmp_root)
        os.makedirs(self.tmp_root, exist_ok=True)

    def tearDown(self):
        for root, dirs, files in os.walk(self.tmp_root, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.tmp_root)

    @patch("subprocess.run")
    def test_grid_sbatch_save_and_read(self, mock_run):
        searcher = SearcherGrid({"--lr": [0.1, 0.01], "--bs": [16, 32]}, runs=2)
        saver: SaverCsv = get_csv_saver(root_dir=self.tmp_root)
        searcher.check_existing_runs(saver)

        sbatch_script = os.path.join("scripts", "sbatch.sh")
        train_script = os.path.join("train.py")
        common_args = {"device": "cpu"}
        sbatchit(train_script, sbatch_script, searcher, cargs=common_args, saver=saver)

        # Expect 8 submissions (4 configs x 2 runs)
        self.assertEqual(mock_run.call_count, 8)

        logger = LoggerDefault()
        logger.log({"acc": 0.7})
        logger.log({"acc": 0.8})
        saver = SaverCsv(logger, params={"--lr": 0.1, "--bs": 16}, root_dir=self.tmp_root)
        saver.save_collated()

        out_params, out_values = saver.read({"--lr": 0.1, "--bs": 16}, "acc", select_by="max", collate_by="mean")
        self.assertEqual(out_params, [["--lr=0.1", "--bs=16"]])
        self.assertEqual(out_values, [0.8])

if __name__ == '__main__':
    unittest.main()
