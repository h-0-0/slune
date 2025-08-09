import unittest
import pandas as pd
from slune.loggers.default import LoggerDefault


class TestLoggerDefaultEdgeCases(unittest.TestCase):
    def test_warning_on_args_ignored(self):
        with self.assertRaises(Warning):
            LoggerDefault(1, x=2)

    def test_read_all_returns_numpy_array(self):
        logger = LoggerDefault()
        df = pd.DataFrame({"m": [1, 3, 2]})
        arr = logger.read_log(df, "m", select_by="all")
        self.assertEqual(arr.tolist(), [1, 3, 2])


if __name__ == "__main__":
    unittest.main()