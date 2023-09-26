import unittest
from unittest.mock import patch
import pandas as pd
from slune.loggers import LoggerDefault
from datetime import datetime
import time

class TestLoggerDefault(unittest.TestCase):
    def setUp(self):
        self.logger = LoggerDefault()
        
    def tearDown(self):
        # Clean up any resources if needed
        pass

    def test_initial_dataframe_empty(self):
        self.assertIsInstance(self.logger.results, pd.DataFrame)
        self.assertTrue(self.logger.results.empty)

    def test_log_method_adds_metrics(self):
        metrics = {'metric1': 42, 'metric2': 99}
        self.logger.log(metrics)
        
        self.assertEqual(len(self.logger.results), 1)
        self.assertSetEqual(set(self.logger.results.columns), set(metrics.keys()))

    def test_log_method_adds_timestamp(self):
        metrics = {'metric1': 42}
        self.logger.log(metrics)
        
        self.assertEqual(len(self.logger.results), 1)
        self.assertTrue('time_stamp' in self.logger.results.columns)

    def test_log_method_adds_correct_values(self):
        from datetime import datetime
        import numpy as np
            
        timestamp = datetime.now()
        metrics = {'metric1': 42, 'metric2': 99}

        # Create a Pandas Timestamp object with the same precision
        rounded_timestamp = pd.Timestamp(timestamp).round('s')

        with patch('time.time', return_value=rounded_timestamp.timestamp()):
            self.logger.log(metrics)

        row = self.logger.results.iloc[0]
        self.assertEqual(row['metric1'], 42)
        self.assertEqual(row['metric2'], 99)
        self.assertEqual(row['time_stamp'].round('s'), rounded_timestamp)


if __name__ == '__main__':
    unittest.main()
