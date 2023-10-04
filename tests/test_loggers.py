import unittest
from unittest.mock import patch
import pandas as pd
from slune.loggers import LoggerDefault
from datetime import datetime
import time

class TestLoggerDefaultWrite(unittest.TestCase):
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


class TestLoggerDefaultRead(unittest.TestCase):
    def setUp(self):
        # Create an instance of LoggerDefault for testing
        self.logger = LoggerDefault()

    def test_read_min_metric(self):
        # Create a sample DataFrame
        data = {'Metric1': [1, 2, 3, 4],
                'Metric2': [5, 6, 7, 8]}
        df = pd.DataFrame(data)

        # Test reading the minimum value of Metric1
        result = self.logger.read_log(df, 'Metric1', min_max='min')
        self.assertEqual(result, 1)

    def test_read_max_metric(self):
        # Create a sample DataFrame
        data = {'Metric1': [1, 2, 3, 4],
                'Metric2': [5, 6, 7, 8]}
        df = pd.DataFrame(data)

        # Test reading the maximum value of Metric2
        result = self.logger.read_log(df, 'Metric2', min_max='max')
        self.assertEqual(result, 8)

    def test_invalid_metric_name(self):
        # Create a sample DataFrame
        data = {'Metric1': [1, 2, 3, 4],
                'Metric2': [5, 6, 7, 8]}
        df = pd.DataFrame(data)

        # Test providing an invalid metric name
        with self.assertRaises(KeyError):
            self.logger.read_log(df, 'InvalidMetric', min_max='min')

    def test_invalid_min_max_argument(self):
        # Create a sample DataFrame
        data = {'Metric1': [1, 2, 3, 4],
                'Metric2': [5, 6, 7, 8]}
        df = pd.DataFrame(data)

        # Test providing an invalid value for min_max argument
        with self.assertRaises(ValueError):
            self.logger.read_log(df, 'Metric1', min_max='invalid_value')


if __name__ == '__main__':
    unittest.main()
