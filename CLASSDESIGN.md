# Class Design
Here we will outline the different kind of classes that are used in slune and how they interact with each other. There are 3 types:
- 'Searcher' classes - these are the classes that are used to define and traverse a search space.
- 'Logger' classes - these are the classes that are used to create and read log files.
- 'Saver' classes - these are the classes that are used to save logs to files and read logs from files.

The base module is where the base classes for each of these types are defined. The base classes are:
- BaseSearcher
- BaseLogger
- BaseSaver

To create a new searcher, logger or saver, you must inherit from the appropriate base class and implement the required methods. The required methods will have the '@abc.abstractmethod' decorator above them and will throw errors if they are not implemented. The compulsory methods allow for well-defined interactions between the different classes and should allow for any combination of searcher, logger and saver to be used together. 

Please read the docs for the base classes to see what methods are required to be implemented and how they should be implemented.