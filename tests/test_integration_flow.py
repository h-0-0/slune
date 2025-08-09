import unittest
from unittest.mock import patch
import os

from slune.slune import sbatchit, get_csv_saver
from slune.searchers.grid import SearcherGrid
from slune.loggers.default import LoggerDefault
from slune.savers.csv import SaverCsv


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
        # Arrange: search space with two params and two runs each
        searcher = SearcherGrid({"--lr": [0.1, 0.01], "--bs": [16, 32]}, runs=2)
        saver: SaverCsv = get_csv_saver(root_dir=self.tmp_root)
        # Before submitting, ensure searcher will skip existing runs if any
        searcher.check_existing_runs(saver)

        # Act: submit jobs (mocked sbatch)
        sbatch_script = os.path.join("scripts", "sbatch.sh")
        train_script = os.path.join("train.py")
        common_args = {"device": "cpu"}
        sbatchit(train_script, sbatch_script, searcher, cargs=common_args, saver=saver)

        # Assert that correct number of submissions are made: there are 4 configs, 2 runs -> 8
        self.assertEqual(mock_run.call_count, 8)

        # Now emulate a training loop writing metrics for one configuration and verify read
        logger = LoggerDefault()
        logger.log({"acc": 0.7})
        logger.log({"acc": 0.8})
        saver = SaverCsv(logger, params={"--lr": 0.1, "--bs": 16}, root_dir=self.tmp_root)
        saver.save_collated()

        # Read back best acc for that params
        out_params, out_values = saver.read({"--lr": 0.1, "--bs": 16}, "acc", select_by="max", collate_by="mean")
        self.assertEqual(out_params, [["--lr=0.1", "--bs=16"]])
        self.assertEqual(out_values, [0.8])


if __name__ == "__main__":
    unittest.main()