import pandas as pd
from slune.base import BaseLogger

class LoggerDefault(BaseLogger):
    """ Logs metric/s in a data frame.
    
    Stores the metric/s in a data frame that we can later save in storage.
    Logs by creating data frame out of the metrics and then appending it to the current results data frame.

    Attributes:
        - results (pd.DataFrame): Data frame containing all the metrics logged so far.
            Each row stores all the metrics that were given in a call to the 'log' method,
            each column title is a metric name.
            The first column is always the time stamp at which 'log' is called.

    """
    
    def __init__(self, *args, **kwargs):
        """ Initialises the logger. """

        super(LoggerDefault, self).__init__(*args, **kwargs)
        # Raise warning if any arguments are given
        if args or kwargs:
            raise Warning(f"Arguments {args} and keyword arguments {kwargs} are ignored")
        # Initialise results data frame
        self.results = pd.DataFrame()
    
    def log(self, metrics: dict):
        """ Logs the metric/s given.

        Stores them in a data frame that we can later save in storage.
        All metrics provided will be saved as a row in the results data frame,
        the first column is always the time stamp at which log is called.

        Args:
            - metrics (dict): Metrics to be logged, keys are metric names and values are metric values.
                Each metric should only have one value! So please log as soon as you get a metric.

        """

        # Get current time stamp
        time_stamp = pd.Timestamp.now()
        # Add time stamp to metrics dictionary
        metrics['time_stamp'] = time_stamp
        # Convert metrics dictionary to a dataframe
        metrics_df = pd.DataFrame(metrics, index=[0])
        # Append metrics dataframe to results dataframe
        self.results = pd.concat([self.results, metrics_df], ignore_index=True)
    
    def read_log(self, data_frame: pd.DataFrame, metric_name: str, select_by: str ='max') -> float:
        """ Reads log and returns value according to select_by.

        Reads the values for given metric for given log and chooses metric value to return based on select_by.

        Args:
            - data_frame (pd.DataFrame): Data frame containing the metric to be read.
            - metric_name (str): Name of the metric to be read.
            - select_by (str, optional): How to select the 'best' metric, currently use ['min', 'max', 'all', 'last', 'first', 'mean', 'median'].

        Returns:
            - value (float): Value of the metric as selected by select_by.
        """ 

        # Get the metric column
        metric_col = data_frame[metric_name]
        # Get the index of the minimum or maximum value
        if select_by == 'max':
            index = metric_col.idxmax()
        elif select_by == 'min':
            index = metric_col.idxmin()
        elif select_by == 'all':
            return metric_col.values
        elif select_by == 'last':
            index = metric_col.index[-1]
        elif select_by == 'first':
            index = metric_col.index[0]
        elif select_by == 'mean':
            return metric_col.mean()
        elif select_by == 'median':
            return metric_col.median()
        else:
            raise ValueError(f"select_by must be one of ['min', 'max', 'all', 'last', 'first', 'mean', 'median'], got {select_by}")
        # Get the value of the metric
        value = metric_col.iloc[index]
        return value