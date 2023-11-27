![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/h-0-0/4aa01e058fee448070c587f6967037e4/raw/CodeCovSlune.json)

![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/h-0-0/4aa01e058fee448070c587f6967037e4/raw/Tests-macos.json)
![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/h-0-0/4aa01e058fee448070c587f6967037e4/raw/Tests-ubuntu.json)
![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/h-0-0/4aa01e058fee448070c587f6967037e4/raw/Tests-windows.json)



# slune (= slurm + tune!)
A super simplistic python package for performing hyperparameter tuning (or more generally launching jobs and saving results) on a cluster using SLURM. Takes advantage of the fact that lots of jobs (including hyperparameter tuning) are embarrassingly parallel! With slune you can divide your compute into lots of separately scheduled jobs meaning that each small job can get running on your cluster more quickly, speeding up your workflow! Often significantly! 

Slune is super-easy to use! We have helper functions which can execute everything you need done for you. Letting you speed up your work without wasting time. 

Slune is barebones by design. This means that you can easily write code to integrate with slune if you want to do something a bit different! You can also workout what each function is doing pretty easily. 

Slune is flexible. In designing this package I've tried to make as few assumptions as possible meaning that it can be used for lots of stuff outside hyperparameter tuning! (or also within!) For example, you can get slune to give you paths for where to save things, submit lots of jobs in parallel for any sort of script and do grid search! and there's more to come!

## Usage
Let's go through a quick example of how we can use slune ... first let's define a model that we want to train:
```python
# Simple Regularized Linear Regression without using external libraries

# Function to compute the mean of a list
def mean(values):
    return sum(values) / float(len(values))

# Function to compute the covariance between two lists
def covariance(x, mean_x, y, mean_y):
    covar = 0.0
    for i in range(len(x)):
        covar += (x[i] - mean_x) * (y[i] - mean_y)
    return covar

# Function to compute the variance of a list
def variance(values, mean):
    return sum((x - mean) ** 2 for x in values)

# Function to compute coefficients for a simple regularized linear regression
def coefficients_regularized(x, y, alpha):
    mean_x, mean_y = mean(x), mean(y)
    var_x = variance(x, mean_x)
    covar = covariance(x, mean_x, y, mean_y)
    b1 = (covar + alpha * var_x) / (var_x + alpha)
    b0 = mean_y - b1 * mean_x
    return b0, b1

# Function to make predictions with a simple regularized linear regression model
def linear_regression_regularized(train_X, train_y, test_X, alpha):
    b0, b1 = coefficients_regularized(train_X, train_y, alpha)
    predictions = [b0 + b1 * x for x in test_X]
    return predictions

# ------------------
# The above is code for a simple normalized linear regression model that we want to train.
# Now let's fit the model and use slune to save how well our model performs!
# ------------------

if __name__ == "__main__":
    # First let's load in the value for the regularization parameter alpha that has been passed to this script from the command line. We will use the slune helper function lsargs to do this. 
    # lsargs returns a tuple of the python path and a list of arguments passed to the script. We can then use this to get the alpha value.
    from slune import lsargs
    python_path, args = lsargs()
    alpha = float(args[0])

    # Mock training dataset, function is y = 1 + 1 * x
    X = [1, 2, 3, 4, 5]
    y = [2, 3, 4, 5, 6]

    # Mock test dataset
    test_X = [6, 7, 8]
    test_y = [7, 8, 9]
    test_predictions = linear_regression_regularized(X, y, test_X, alpha)

    # First let's load in a function that we can use to get a saver object that uses the default method of logging (we call this object a slog = saver + logger). The saving will be coordinated by a csv saver object which saves and reads results from csv files stored in a hierarchy of directories.
    from slune import get_csv_slog
    csv_slog = get_csv_slog(params = args)

    # Let's now calculate the mean squared error of our predictions and log it!
    mse = mean((test_y[i] - test_predictions[i])**2 for i in range(len(test_y)))
    csv_slog.log({'mse': mse})

    # Let's now save our logged results!
    slog.save_collated()
```
Now let's write some code that will submit some jobs to train our model using different hyperparameters!!
```python
# Let's now load in a function that will coordinate our search! We're going to do a grid search.
# SearcherGrid is the class we can use to coordinate a grid search. We pass it a dictionary of hyperparameters and the values we want to try for each hyperparameter. We also pass it the number of runs we want to do for each combination of hyperparameters.
from slune.searchers import SearcherGrid
grid_searcher = SearcherGrid({'alpha' : [0.25, 0.5, 0.75]}, runs = 1)

# Let's now import a function which will submit a job for our model, the script_path specifies the path to the script that contains the model we want to train. The template_path specifies the path to the template script that we want to specify the job with, cargs is a list of constant arguments we want to pass to the script for each tuning. 
# We set slog to None as we don't want to not run jobs if we have already run them before.
from slune import sbatchit
script_path = 'model.py'
template_path = 'template.sh'
sbatchit(script_path, template_path, grid_searcher, cargs=[], slog=None)
```
Now we've submitted our jobs we will wait for them to finish 🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛, now that they are finished we can read the results!
```python
from slune import get_csv_slog
csv_slog = get_csv_slog(params = None)
params, value = csv_slog.read(params = [], metric_name = 'mse', select_by ='min')
print(f'Best hyperparameters: {params}')
print(f'Their MSE: {value}')
```
Amazing! 🥳 We have successfully used slune to train our model. I hope this gives you a good flavour of how you can use slune and how easy it is to use!

Please check out the examples folder for notebooks detailing in more depth some potential ways you can use slune. The docs are not yet up and running 😢 but they are coming soon!

## Roadmap
- Make package user friendly:
    - Add github workflows to automate testing, check code coverage etc. 
    - Go through automation settings.
    - Add documentation.
    - Add to pypi.
Still in early stages! First thing on the horizon is better integration with SLURM:
- Set-up notifications for job completion, failure, etc.
- Auto job naming, job output naming and job output location saving.
- Auto save logged results when finishing a job.
- Automatically re-submit failed jobs.
- Tools for monitoring and cancelling jobs. 
Then it will be looking at adding more savers, loggers and searchers! For example integration with tensorboard, saving to one csv file (as opposed to a hierarchy of csv files in different directories) and different search methods like random search and cross validation. Finally, more helper functions!

However, I am trying to keep this package as bloatless as possible to make it easy for you to tweak and configure to your individual needs. It's written in a simple and compartmentalized manner for this reason. You can of course use the helper functions and let slune handle everything under the hood, but, you can also very quickly and easily write your own classes to work with other savers, loggers and searchers to do as you please.

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