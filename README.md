# slune (= slurm + tune!)
A super simplistic way to perform hyperparameter tuning on a cluster using SLURM. Will submit a seperate job script for each run in the tuning and store metrics in a csv and then allow you to easily query for the best hyperparamters based on metric.

## Usage
So early I haven't even written the docs yet! Will be adding a quick example here soon along with examples in an example folder. Later on will add a full documentation.

## Coming soon
Currently very much in early stages, first things still to do, in order of priority:
- Make package user friendly:
    - Refine package structure (should be able to import without specifiying file).
    - Add github workflows to automate testing, check code coverage etc. 
    - Add integration testing.
    - Add documentation.
- For SaverCSV add constant parameter checking (add log with all parameters and check they remain the same, return error if so). 
- Better integration with SLURM:
    - Set-up notifications for job completion, failure, etc.
    - Auto job naming, job output naming and job output location saving.
    - Auto save logged results when finishing a job.
    - Automatically re-submit failed jobs.
    - Tools for monitoring and cancelling jobs. 
- Add some more classes for saving job results in different ways and for different tuning methods (eg. with tensorboard, non-hierarchical csv, etc.).

Although the idea for this package is to keep it ultra bare-bones and make it easy for the user to modify and add things themselves to their liking.

## Installation
To install latest version use:
```bash
pip install slune-lib
```
To install latest dev version use (CURRENTLY RECOMENDED):
```bash
# With https
pip install "git+https://github.com/h-aze/slune.git#egg=slune-lib"
```