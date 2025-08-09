import unittest
import os
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault


class TestSaverExtPathNumbering(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_directory"
        if os.path.isdir(self.test_dir):
            for root, dirs, files in os.walk(self.test_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.test_dir)
        os.makedirs(self.test_dir)

    def tearDown(self):
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_results_numbering_increments(self):
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        p = {"--a": 1}
        path0 = saver.get_path(["--a=1"])  # no file exists yet
        self.assertTrue(path0.endswith(os.path.join("--a=1", "results_0.csv")))
        # create file then ask again
        os.makedirs(os.path.dirname(path0), exist_ok=True)
        with open(path0, "w") as f:
            f.write("")
        path1 = saver.get_path(["--a=1"])  # should now be results_1
        self.assertTrue(path1.endswith(os.path.join("--a=1", "results_1.csv")))

    def test_results_prefix_validation(self):
        # If a file with wrong prefix exists, get_path should raise
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        bad_dir = os.path.join(self.test_dir, "--a=1")
        os.makedirs(bad_dir, exist_ok=True)
        # create a wrong-named ext file
        with open(os.path.join(bad_dir, "badname.csv"), "w") as f:
            f.write("")
        with self.assertRaises(ValueError):
            saver.get_path(["--a=1"])  


if __name__ == "__main__":
    unittest.main()