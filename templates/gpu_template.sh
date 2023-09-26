#!/bin/bash
#SBATCH --job-name=my_job_name         # Job name
#SBATCH --output=my_job_output.log     # Output file (stdout)
#SBATCH --error=my_job_error.log       # Error file (stderr)
#SBATCH --partition=gpu                # Specify the partition/queue name
#SBATCH --nodes=1                      # Number of nodes
#SBATCH --ntasks=1                     # Number of tasks (cores)
#SBATCH --cpus-per-task=1              # Number of CPU cores per task
#SBATCH --gres=gpu:1                   # Define number of GPUs per node, can also define type of GPU eg. gpu:tesla, gpu:k80, gpu:p100, gpu:v100
#SBATCH --mem-per-gpu=1G               # Define memory per GPU
#SBATCH --time=01:00:00                # Wall time (hh:mm:ss)
#SBATCH --mail-user=your@email.com     # Email address for job notifications
#SBATCH --mail-type=ALL                # Email notifications (BEGIN, END, FAIL)

# Define executable
export EXE=/bin/hostname

# Optional: Load necessary modules or set environment variables
# module load your_module
# export YOUR_VARIABLE=value

# Change to your working directory
cd "${SLURM_SUBMIT_DIR}"

# Execute code
${EXE}

# Print some usefull stuff!
echo JOB ID: ${SLURM_JOBID}
echo Working Directory: $(pwd)
echo Start Time: $(date)

# Print GPU information
nvidia-smi --query-gpu=name --format=csv,noheader

# Activate virtual environment (if you have one), change the path to match the location of your virtual environment
source ../pyvenv/bin/activate

# Where we run the script to perform training run with model, 
# first argument to this job script will be the python script to run,
# the rest of the arguments passed to the job script will be passed as arguments to the python script
python $1 ${@:2}

# End of job script, let's print the time at which we finished
echo End Time: $(date)