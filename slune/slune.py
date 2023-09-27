from argparse import ArgumentParser
import subprocess
import sys

from slune.base import Slog
from slune.savers import SaverCsv
from slune.loggers import LoggerDefault

def submit_job(sh_path, args):
    """
    Submits a job using the Bash script at sh_path,
    args is a list of strings containing the arguments to be passed to the Bash script.
    """
    try:
        # Run the Bash script using subprocess
        command = [sh_path] + args
        subprocess.run(['sbatch'] + command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running sbatch: {e}")

def sbatchit(script_path, template_path, searcher, cargs=[]):
    """
    Carries out hyper-parameter tuning by submitting a job for each set of hyper-parameters given by tune_control, 
    for each job runs the script stored at script_path with selected hyper-parameter values and the arguments given by cargs.
    Uses the template file with path template_path to guide the creation of the sbatch script for each job. 
    Args:
        - script_path (string): Path to the script (of the model) to be run for each job.

        - template_path (string): Path to the template file used to create the sbatch script for each job.

        - cargs (list): List of strings containing the arguments to be passed to the script for each job. 
                        Must be a list even if there is just one argument, default is empty list.

        - tuning (Tuning): Tuning object used to select hyper-parameter values for each job.
    """
    # Create sbatch script for each job
    for _ in range(len(searcher)):
        # Get argument for this job
        args = searcher.next_tune()
        # Submit job
        submit_job(template_path, [script_path] + cargs + args)
    print("Submitted all jobs!")

def lsargs():
    """
    Returns the script name and a list of the arguments passed to the script.
    """
    args = sys.argv
    return args[0], args[1:]

def garg(args, arg_names):
    """
    Finds the argument with name arg_names (if its a string) in the list of arguments args_ls and returns its value.
    If arg_names is a list of strings then returns a list of the values of the argument names in arg_names.
    """
    def single_garg(arg_name):
        # Find index of argument
        arg_index = [i for i, arg in enumerate(args) if arg_name in arg]
        # Return value error if argument not found
        if not arg_index:
            raise ValueError(f"Argument {arg_name} not found in arguments {args}")
        # Return value of argument
        return args[arg_index].split("=")[1]
    if type(arg_names) == list:
        return [single_garg(arg_name) for arg_name in arg_names]
    else:
        return single_garg(arg_names)

def get_slogcsv(params):
    """
    Creates a Slog object from the SaverCsv and LoggerDefault classes.
    """
    return Slog(LoggerDefault(), SaverCsv(params))

# TODO: add functions for reading results