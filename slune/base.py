
class Searcher():
    """
    Class that creates search space and returns arguments to pass to sbatch script
    """
    def __init__(self):
        pass

    def __len__(self):
        """
        Returns the number of hyperparameter configurations to try.
        """
        return len(self.searcher)
    
    def next_tune(self, args, kwargs):
        """
        Returns the next hyperparameter configuration to try. 
        """
        return self.searcher.next_tune(args, kwargs)

class Slog():
    """
    Class used to log metrics during tuning run and to save the results.
    Args:
        - Logger (object): Class that handles logging of metrics, including the formatting that will be used to save and read the results.
        - Saver (object): Class that handles saving logs from Logger to storage and fetching correct logs from storage to give to Logger to read.
    """
    def __init__(self, Logger, Saver):
        self.logger = Logger
        self.saver = Saver # TODO: Have to instantiate this with params, is there way you can just define the class?
    
    def log(self, args, kwargs):
        """
        Logs the metric/s for the current hyperparameter configuration, 
        stores them in a data frame that we can later save in storage.
        """
        self.logger.log(args, kwargs)
        
    def save_collated(self, args, kwargs):
        """
        Saves the current results in logger to storage.
        """
        self.saver.save_collated(self.logger.results, args, kwargs)
    
    def read(self, args, kwargs):
        """
        Reads results from storage.
        """
        return self.saver.read(args, kwargs)


