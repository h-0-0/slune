import pandas as pd
from slune.base import BaseLogger

class LoggerDefault(BaseLogger):
    """
    Logs the metric/s for the current hyperparameter configuration, 
    stores them in a data frame that we can later save in storage.
    """
    def __init__(self, *args, **kwargs):
        super(LoggerDefault, self).__init__(*args, **kwargs)
        self.results = pd.DataFrame()
    
    def log(self, metrics: dict):
        """
        Logs the metric/s for the current hyperparameter configuration, 
        stores them in a data frame that we can later save in storage.
        All metrics provided will be saved as a row in the results data frame,
        the first column is always the time stamp at which log is called.
        Args:
            - metrics (dict): Dictionary of metrics to be logged, keys are metric names and values are metric values.
                              Each metric should only have one value! So please log as soon as you get a metric
        """
        # Get current time stamp
        time_stamp = pd.Timestamp.now()
        # Add time stamp to metrics dictionary
        metrics['time_stamp'] = time_stamp
        # Convert metrics dictionary to a dataframe
        metrics_df = pd.DataFrame(metrics, index=[0])
        # Append metrics dataframe to results dataframe
        self.results = pd.concat([self.results, metrics_df], ignore_index=True)
    
    def read_log(self, data_frame: pd.DataFrame, metric_name: str, min_max: str ='max'):
        """
        Reads the minimum or maximum value of a metric from a data frame.
        Args:
            - data_frame (pd.DataFrame): Data frame containing the metric to be read.
            - metric_name (string): Name of the metric to be read.
            - min_max (string): Whether to read the minimum or maximum value of the metric, default is 'max'.
        Returns:
            - value (float): Minimum or maximum value of the metric.
        """ 
        # Get the metric column
        metric_col = data_frame[metric_name]
        # Get the index of the minimum or maximum value
        if min_max == 'max':
            index = metric_col.idxmax()
        elif min_max == 'min':
            index = metric_col.idxmin()
        else:
            raise ValueError(f"min_max must be 'min' or 'max', got {min_max}")
        # Get the value of the metric
        value = metric_col.iloc[index]
        return value