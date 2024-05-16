from typing import List, Optional, Tuple
from slune.base import BaseSearcher, BaseSaver
import subprocess
import sys
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault
from slune.utils import dict_to_strings

def submit_job(sh_path: str, script_path:str = None , args: dict = {}):
    """ Submits a job using specified Bash script.

    Args:
        - sh_path (string): Path to the Bash script to be run.

        - script_path (string): Path to the script (of the model) to be run for each job, default is None.

        - args (dict): Contains (key, value) pairs for all the arguments to be passed to the Bash script.
    
    """
    
    args = dict_to_strings(args, ready_for_cl=True)
    try:
        # Run the Bash script using subprocess
        if script_path == None:
            command = [sh_path] + args
        else:
            command = [sh_path, script_path] + args
        subprocess.run(['sbatch'] + command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running sbatch: {e}")

def sbatchit(script_path: str, sbatch_path: str, searcher: BaseSearcher, cargs: Optional[dict]={}, saver: Optional[BaseSaver]=None):
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

        - cargs (dict, optional): Contains arguments to be passed to the script for every job.

        - saver (Saver, optional): Saver object used if we want to check if there are existing runs so we don't rerun.
            Can simply not give a Saver object if you want to rerun all jobs.

    """

    if saver != None:
        searcher.check_existing_runs(saver)
    # Create sbatch script for each job
    for args in searcher:
        # Submit job
        d = dict(cargs, **args)
        submit_job(sbatch_path, script_path, d)

def lsargs() -> Tuple[str, List[str]]:
    """ Returns the script name and the list of the arguments passed to the script.
    
    Returns:
        - script_name (str): Name of the script.

        - args (list of str): List of strings containing the arguments passed to the script.
        
    """

    args = sys.argv
    return args[0], args[1:]

def get_csv_saver(params: Optional[dict]= None, root_dir: Optional[str]='slune_results') -> BaseSaver:
    """ Returns a SaverCsv object with the given parameters and root directory.

    Args:
        - params (dict, optional): Dictionary of parameters to be passed to the SaverCsv object, default is None.

        - root_dir (str, optional): Path to the root directory to be used by the SaverCsv object, default is 'slune_results'.

    Returns:
        - SaverCsv (Saver): Saver object with the given parameters and root directory.
            Initialized with a LoggerDefault object as its logger.
    
    """

    return SaverCsv(LoggerDefault(), params = params, root_dir=root_dir)
