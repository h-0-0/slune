from argparse import ArgumentParser
import subprocess

def submit_job(sh_path, args):
    """
    Submits a job using the Bash script at sh_path,
    args is a list of strings containing the arguments to be passed to the Bash script.
    """
    try:
        # Run the Bash script using subprocess
        command = ['bash', sh_path] + args
        subprocess.run(['sbatch', command], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running sbatch: {e}")

def sbatchit(script_path, template_path, tuning, cargs=[]):
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
    for i in range(len(tuning)):
        # Get argument for this job
        args = tuning.next_tune()
        # Submit job
        submit_job(template_path, [script_path] + cargs + args)
    print("Submitted all jobs!")

# TODO: add functions for reading results
