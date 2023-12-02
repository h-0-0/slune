from typing import List, Optional, Union
from slune.base import BaseSearcher, BaseSaver
import subprocess
import sys
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault

def submit_job(sh_path: str, args: List[str]):
    """ Submits a job using specified Bash script

    Args:
        - sh_path (string): Path to the Bash script to be run.

        - args (list of str): List of strings containing the arguments to be passed to the Bash script.
    
    """

    try:
        # Run the Bash script using subprocess
        command = [sh_path] + args
        subprocess.run(['sbatch'] + command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running sbatch: {e}")

def sbatchit(script_path: str, sbatch_path: str, searcher: BaseSearcher, cargs: Optional[List]=[], saver: Optional[BaseSaver]=None):
    """ Submits jobs based on arguments given by searcher.

    For each job runs the script stored at script_path with selected parameter values given by searcher
    and the arguments given by cargs.

    Uses the sbatch script with path sbatch_path to submit each job to the cluster. 

    If given a Saver object, uses it to check if there are existing runs for each job and skips them,
    based on the number of runs we would like for each job (which is stored in the saver).

    Args:
        - script_path (str): Path to the script (of the model) to be run for each job.

        - sbatch_path (str): Path to the sbatch script that will be used to submit each job.
            Examples of sbatch scripts can be found in the templates folder.

        - searcher (Searcher): Searcher object used to retrieve changing arguments for each job.

        - cargs (list, optional): Contains arguments to be passed to the script for every job.

        - saver (Saver, optional): Saver object used if we want to check if there are existing runs so we don't rerun.
            Can simply not give a Saver object if you want to rerun all jobs.

    """

    if saver != None:
        searcher.check_existing_runs(saver)
    # Create sbatch script for each job
    for args in searcher:
        # Submit job
        submit_job(sbatch_path, [script_path] + cargs + args)

def lsargs() -> (str, List[str]):
    """ Returns the script name and a list of the arguments passed to the script."""
    args = sys.argv
    return args[0], args[1:]

def garg(args: List[str], arg_names: Union[str, List[str]]) -> Union[str, List[str]]:
    """ Finds the argument/s with name arg_names in the list of arguments args_ls and returns its value/s.
    
    Args:
        - args (list of str): List of strings containing the arguments to be searched.

        - arg_names (str or list of str): String or list of strings containing the names of the arguments to be searched for.       

    Returns:
        - arg_value (str or list of str): String or list of strings containing the values of the arguments found.

    """

    def single_garg(arg_name):
        # Check if arg_name is a string
        if type(arg_name) != str:
            raise TypeError(f"arg_name must be a string, got {type(arg_name)}")
        # Find index of argument
        arg_index = [i for i, arg in enumerate(args) if arg_name in arg]
        # Return value error if argument not found
        if not arg_index:
            raise ValueError(f"Argument {arg_name} not found in arguments {args}")
        # Return value of argument
        if len(arg_index) > 1:
            raise ValueError(f"Multiple arguments with name {arg_name} found in arguments {args}")
        return args[arg_index[0]].split("=")[1]
    if type(arg_names) == list:
        return [single_garg(arg_name) for arg_name in arg_names]
    else:
        return single_garg(arg_names)

def get_csv_slog(params: Optional[dict]= None, root_dir: Optional[str]='slune_results') -> BaseSaver:
    """ Returns a SaverCsv object with the given parameters and root directory.

    Args:
        - params (dict, optional): Dictionary of parameters to be passed to the SaverCsv object, default is None.

        - root_dir (str, optional): Path to the root directory to be used by the SaverCsv object, default is 'slune_results'.

    Returns:
        - SaverCsv (Saver): Saver object with the given parameters and root directory.
            Initialized with a LoggerDefault object as its logger.
    
    """

    return SaverCsv(LoggerDefault(), params = params, root_dir=root_dir)
