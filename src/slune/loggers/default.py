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
            - select_by (str, optional): How to select the 'best' metric, currently can select by 'min' or 'max'.

        Returns:
            - value (float): Minimum or maximum value of the metric.

        TODO: 
            - Add more options for select_by.
            - Should be able to return other types than float?

        """ 

        # Get the metric column
        metric_col = data_frame[metric_name]
        # Get the index of the minimum or maximum value
        if select_by == 'max':
            index = metric_col.idxmax()
        elif select_by == 'min':
            index = metric_col.idxmin()
        else:
            raise ValueError(f"select_by must be 'min' or 'max', got {select_by}")
        # Get the value of the metric
        value = metric_col.iloc[index]
        return value