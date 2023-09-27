import pandas as pd

class LoggerDefault():
    """
    Logs the metric/s for the current hyperparameter configuration, 
    stores them in a data frame that we can later save in storage.
    """
    def __init__(self):
        self.results = pd.DataFrame()
    
    def log(self, metrics):
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
    
    def read_log(self, *args, **kwargs):
        # TODO: implement this function
        raise NotImplementedError