import abc 
from typing import Type

class BaseSearcher(metaclass=abc.ABCMeta):
    """
    Base class for all searchers. Which should be subclassed to implement different search algorithms.
    Must implement __len__ and next_tune methods.
    """
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass
    
    @abc.abstractmethod
    def __len__(self, *args, **kwargs):
        """
        Returns the number of hyperparameter configurations to try.
        """
        pass
    
    @abc.abstractmethod
    def next_tune(self, *args, **kwargs):
        """
        Returns the next hyperparameter configuration to try. 
        """
        pass

    @abc.abstractmethod
    def check_existing_runs(self, *args, **kwargs):
        """
        Used to tell searcher to check if there are existing runs in storage, this will probably require giving a Saver object.
        """
        pass

    def __iter__(self):
        """
        Makes the searcher iterable, so we can use it in a for loop.
        """
        return self
    
    def __next__(self):
        """
        Makes the searcher iterable, so we can use it in a for loop.
        """
        try:
            return self.next_tune()
        except:
            raise StopIteration

class BaseLogger(metaclass=abc.ABCMeta):
    """
    Base class for all loggers. Which should be subclassed to implement different logging algorithms.
    Must implement log and read_log methods.
    """
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass
    
    @abc.abstractmethod
    def log(self, *args, **kwargs):
        """
        Logs the metric/s for the current hyperparameter configuration, 
        stores them in a data frame that we can later save in storage.
        You can use this method directly form your saver object (inheriting from BaseSaver) that you instantiate with a BaseLogger subclass object.
        """
        pass
    
    @abc.abstractmethod
    def read_log(self, *args, **kwargs):
        """
        Reads the minimum or maximum value of a metric from a data frame.
        You can use this method directly form your saver object (inheriting from BaseSaver) that you instantiate with a BaseLogger subclass object.
        """
        pass

class BaseSaver(metaclass=abc.ABCMeta):
    """
    Base class for all savers. Which should be subclassed to implement different saving algorithms.
    Must implement save_collated and read methods. Inherits from BaseLogger.
    """
    @abc.abstractmethod
    def __init__(self, logger_instance: BaseLogger, *args, **kwargs):
        # Given a class that inherits from BaseLogger we make it accessible through self.logger and make its methods accessible through self.log and self.read_log
        self.logger = logger_instance
        self.log = self.logger.log
        self.read_log = self.logger.read_log

    @abc.abstractmethod
    def save_collated(self, *args, **kwargs):
        """
        Saves the current results in logger to storage.
        """
        pass
    
    @abc.abstractmethod
    def read(self, *args, **kwargs):
        """
        Reads results from storage.
        """
        pass

    @abc.abstractmethod
    def exists(self, *args, **kwargs):
        """
        Checks if results already exist in storage, should return integer indicating the number of runs that exist in storage for the given parameters. 
        """
        pass
