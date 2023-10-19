# slune (= slurm + tune!)
A super simplistic way to perform hyperparameter tuning on a cluster using SLURM. Will submit a seperate job script for each run in the tuning and store metrics in a csv and then allow you to easily query for the best hyperparamters based on metric.

## Usage
So early I haven't even written the docs yet! Will be adding a quick example here soon along with examples in an example folder. Later on will add a full documentation.

## Coming soon
Currently very much in early stages, first things still to do:
- Need to create root directory before submitting job scripts? how do I stop different scripts creating directories at same time and resulting errors?
- What happens if multiple results files? reading from them and not rerunning jobs already done.
    - Get Searcher to check which tunings have been done and which haven't and only submit the ones that haven't been done yet. Depending on a flag, ie. if you want to re-run a tuning you can set a flag to re-run all tunings.

- Refine package structure (should be able to import without specifiying file) and sort out github actions like test coverage, running tests etc.
- Add more tests (including integration tests) and documentation.
- Emails for when tuning done?
- Auto sbatch job naming and job output naming.
- Auto save when finished a tuning run.
- Add interfacing with SLURM to check for and re-submit failed jobs etc. 
- Cancelling submitted jobs quickly and easily.
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
```