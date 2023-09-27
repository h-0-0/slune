# slune (= slurm + tune!)
A super simplistic way to perform hyperparameter tuning on a cluster using SLURM. Will submit a seperate job script for each run in the tuning and store metrics in a csv and then allow you to easily query for the best hyperparamters based on metric.

## Usage
So early I haven't even written the docs yet! Will be adding a quick example here soon along with examples in an example folder. Later on will add a full documentation.

## Coming soon
Currently very much in early stages, first things still to do:
- Auto save when finished a tuning run.
- Auto sbatch job naming and job output naming.
- Add ability to read results, currently can only submit jobs and log metrics during tuning.
- Refine class structure, ie. subclassing, making sure classes have essential methods, what are the essential methods and attributes? etc.
- Refine package structure and sort out github actions like test coverage, running tests etc.
- Add interfacing with SLURM to check for and re-submit failed jobs etc. 
- Add more tests and documentation.
- Add some more subclasses for saving job results in different ways and for different tuning methods. 
Although the idea for this package is to keep it ultra bare-bones and make it easy for the user to mod and add things themselves to their liking.

## Installation
To install latest version use:
```bash
pip install slune-lib
```
To install latest dev version use:
```bash
# With https
pip install "git+https://github.com/h-aze/slune.git#egg=slune-lib"
# or with SSH
pip install "git+ssh://@github.com:h-aze/slune.git#egg=slune-lib"
```