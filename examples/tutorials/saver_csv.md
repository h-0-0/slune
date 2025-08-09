# Saver tutorial: SaverCsv

Savers persist run results to storage and can read them back. `SaverCsv` writes log rows to CSV files in a parameter-structured directory hierarchy and can query the best values across runs.

## What it does
- Coordinates with a Logger (e.g., `LoggerDefault`) to save results to CSV
- Creates a directory tree from parameters like `--param=value` and stores files as `results_<n>.csv`
- Prevents clobbering by incrementing `<n>` when results already exist
- Reads values across one or multiple runs and aggregates via `collate_by` (e.g., mean)
- Counts existing runs with `exists(params)`

## Directory structure
- Root directory defaults to `./slune_results` (customizable via `root_dir`)
- For params `{alpha: 0.1, batch_size: 32}`, paths look like:
  - `slune_results/--alpha=0.1/--batch_size=32/results_0.csv`
- If a path exists, next save becomes `results_1.csv`, etc.

## Quick start
```python
from slune import get_csv_saver  # builds SaverCsv(LoggerDefault())

# Provide params now or later (can be None). These define where results are saved.
saver = get_csv_saver(params={"alpha": 0.1, "batch_size": 32}, root_dir="slune_results")

# Log metrics via the attached logger
saver.log({"mse": 0.42})
saver.log({"mse": 0.38})

# Persist to CSV
saver.save_collated()  # writes results_<n>.csv under the parameterized path
```

## Reading results across runs
`read(params, metric_name, select_by, collate_by)` searches all matching CSVs and returns:
- a list of parameter paths and a list of values (potentially more than one if multiple paths match)

```python
from slune import get_csv_saver
saver = get_csv_saver(root_dir="slune_results")  # params can be None to search all

# Example: best MSE across all runs matching alpha=0.1
params, values = saver.read(params={"alpha": 0.1}, metric_name="mse", select_by="min", collate_by="mean")
print(params)   # e.g., [["alpha=0.1", "batch_size=32"]]
print(values)   # e.g., [0.36]

# All values from each matching CSV (no averaging)
params, values = saver.read(params={"alpha": 0.1}, metric_name="mse", select_by="all", collate_by="all")
```

- **select_by**: one of `min`, `max`, `last`, `first`, `mean`, `median`, `all` (applies per CSV DataFrame via the Logger)
- **collate_by**: `mean` (average across multiple runs with the same params) or `all` (return each CSV’s value/series)

## Counting existing runs (for skipping)
```python
# How many CSVs are stored for these params?
num_runs = saver.exists({"alpha": 0.1, "batch_size": 32})
```

## Advanced: changing or generating paths
```python
# Update current path and optionally save prior results first
saver.getset_current_path(params={"alpha": 0.2, "batch_size": 64}, save=True)
# Now saver.current_path points to the next results_<n>.csv under the new param path
```

Notes:
- Parameter values are normalized numerically so `--alpha=0.10` and `--alpha=0.1` match.
- If `params` is `{}` or `None`, `read` searches all CSVs in the root.