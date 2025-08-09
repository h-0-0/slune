# Tutorial: Combining Searcher, Logger, and Saver

This guide shows an end-to-end flow:
- Generate configs with `SearcherGrid`
- Log metrics with `LoggerDefault` via `SaverCsv`
- Save results to CSVs
- Optionally submit jobs with SLURM using `sbatchit`

## End-to-end example (single-process)
```python
from slune.searchers.grid import SearcherGrid
from slune import get_csv_saver

# 1) Build the grid of configs
searcher = SearcherGrid({"alpha": [0.25, 0.5, 0.75]}, runs=1)

# 2) Create a saver that uses the default logger
saver = get_csv_saver(root_dir="slune_results")

# 3) Iterate configs, run your experiment, log metrics, then save
for cfg in searcher:
    # Run your training/eval code here using cfg
    alpha = cfg["alpha"]
    # ... compute a metric (mocked):
    mse = (1.0 - alpha) ** 2

    # Log one or more metrics
    saver.log({"mse": mse})

    # Save current run results to CSV
    # You can pass params to determine the save path for this run
    saver.getset_current_path(params=cfg, save=False)  # sets path for this run
    saver.save_collated()
```

- This creates parameterized directories like `slune_results/--alpha=0.25/` and CSVs named `results_<n>.csv`.

## Reading results later
```python
from slune import get_csv_saver
saver = get_csv_saver(root_dir="slune_results")

# Best (lowest) MSE for alpha=0.5
params, values = saver.read(params={"alpha": 0.5}, metric_name="mse", select_by="min", collate_by="mean")
print(params, values)

# Best overall (search all)
params_all, values_all = saver.read(params={}, metric_name="mse", select_by="min", collate_by="mean")
print(params_all, values_all)
```

## Submitting jobs with SLURM (multi-process)
Use `sbatchit` to submit jobs for each config using your own `model.py` and a SLURM script like `template.sh`.
```python
from slune import sbatchit
from slune.searchers.grid import SearcherGrid

searcher = SearcherGrid({"alpha": [0.25, 0.5, 0.75]}, runs=1)

script_path = "model.py"     # your python training script
sbatch_path = "template.sh"   # your SLURM submission script

# Optional: attach a saver to skip configs already having results
# from slune import get_csv_saver
# saver = get_csv_saver(root_dir="slune_results")
# searcher.check_existing_runs(saver)

sbatchit(script_path, sbatch_path, searcher, cargs={}, saver=None)
```

Inside your `model.py`, consume CLI args and save results:
```python
# model.py
from slune import lsargs, get_csv_saver

if __name__ == "__main__":
    _, args = lsargs()   # list like ["--alpha=0.25", ...]

    # Convert to dict if desired
    from slune.utils import strings_to_dict
    cfg = strings_to_dict(args)
    alpha = float(cfg["alpha"])  # run your training using cfg

    # Compute metric (mock)
    mse = (1.0 - alpha) ** 2

    # Save
    saver = get_csv_saver(params=cfg, root_dir="slune_results")
    saver.log({"mse": mse})
    saver.save_collated()
```

Tips:
- Keep per-run logging simple: call `log` as soon as you have metric values.
- Use `exists(params)` with the Searcher to skip already-finished configs when re-running experiments.