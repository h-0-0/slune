import abc 

class BaseSearcher(metaclass=abc.ABCMeta):
    """ Base class for all Searchers. 
    
    This must be subclassed to create different Searcher classes.
    Please name your searcher class Searcher<SearcherName>
    Outlines a protocol for creating a search space and creating configurations from it.
    Methods document what they should do once implemented. 

    """
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        """ Initialises the searcher. """

        pass
    
    @abc.abstractmethod
    def __len__(self, *args, **kwargs):
        """ Returns the number of configurations defined by the search space of the searcher. """

        pass
    
    @abc.abstractmethod
    def next_tune(self, *args, **kwargs):
        """ Returns the next configuration to try. """

        pass

    @abc.abstractmethod
    def check_existing_runs(self, *args, **kwargs):
        """ Used to tell searcher to check if there are existing runs in storage.

        If there are existing runs, the searcher should skip them 
        based on the number of runs we would like for each job.
        This may require a 'runs' attribute to be set in the searcher.
        It will probably also require access to a Saver object,
        so we can use it's saving protocol to check if there are existing runs.
        In this case is advised that this function takes a Saver object as an argument,
        and that the searcher is initialized with a 'runs' attribute.

        """

        pass

    def __iter__(self):
        """ Makes the searcher iterable, so we can use it in a for loop.
        
        Feel free to override this method if needed.

        """

        return self
    
    def __next__(self):
        """ Makes the searcher iterable, so we can use it in a for loop.

        Feel free to override this method if needed.

        """

        try:
            return self.next_tune()
        except:
            raise StopIteration

class BaseLogger(metaclass=abc.ABCMeta):
    """ Base class for all Loggers. 
    
    This must be subclassed to implement different Logger classes.
    Please name your logger class Logger<LoggerName>.
    Outlines a protocol for logging metrics and reading from the logs.
    Methods document what they should do once implemented. 

    """
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        """ Initialises the logger. """

        pass
    
    @abc.abstractmethod
    def log(self, *args, **kwargs):
        """ Logs the metric/s for the current hyperparameter configuration.

        Should store metrics in some way so we can later save it using a Saver.

        """

        pass
    
    @abc.abstractmethod
    def read_log(self, *args, **kwargs):
        """ Returns value of a metric from the log based on a selection criteria. """

        pass

class BaseSaver(metaclass=abc.ABCMeta):
    """ Base class for all savers. 
    
    This must be subclassed to implement different Saver classes.
    Please name your saver class Saver<SaverName>.
    Outlines a protocol for saving and reading results to/from storage.
    Methods document what they should do once implemented. 

    """

    @abc.abstractmethod
    def __init__(self, logger_instance: BaseLogger, *args, **kwargs):
        """ Initialises the saver.

        Assigns the logger instance to self.logger and makes its methods accessible through self.log and self.read_log.

        Args:
            - logger_instance (BaseLogger): Instance of a logger class that inherits from BaseLogger.
        
        """

        # Given a class that inherits from BaseLogger we make it accessible through self.logger and make its methods accessible through self.log and self.read_log
        self.logger = logger_instance
        self.log = self.logger.log
        self.read_log = self.logger.read_log

    @abc.abstractmethod
    def save_collated(self, *args, **kwargs):
        """ Saves the current results in logger to storage. """

        pass
    
    @abc.abstractmethod
    def read(self, *args, **kwargs):
        """ Reads results from storage. """

        pass

    @abc.abstractmethod
    def exists(self, *args, **kwargs):
        """ Checks if results already exist in storage.
         
        Should return integer indicating the number of runs that exist in storage for the given parameters. 

        """

        pass
