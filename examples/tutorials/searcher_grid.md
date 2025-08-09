# Searcher tutorial: SearcherGrid

A Searcher generates parameter configurations to try. `SearcherGrid` exhaustively enumerates combinations from a dictionary of parameter values and can repeat each configuration multiple times via `runs`.

## What it does
- Expands a dict like `{ "alpha": [0.1, 0.2], "batch": [32, 64] }` into a full grid
- Iterates configurations via `for cfg in searcher: ...` or `.next_tune()`
- Optionally repeats each configuration `runs` times
- Can skip configurations that already have `runs` saved, when linked to a Saver

## Quick start
```python
from slune.searchers.grid import SearcherGrid

# Try all pairs of alpha and batch. Repeat each config twice.
searcher = SearcherGrid(configs={"alpha": [0.1, 0.2], "batch": [32, 64]}, runs=2)

for config in searcher:
    # config is a dict like {"alpha": 0.1, "batch": 32}
    print(config)
```

## Skipping existing runs
To skip re-running configurations that already have results saved, attach a Saver with `check_existing_runs`. The Searcher will call the Saver’s `exists(params)` under the hood and skip any config that already has at least `runs` saved.

```python
from slune import get_csv_saver
from slune.searchers.grid import SearcherGrid

searcher = SearcherGrid({"alpha": [0.1, 0.2]}, runs=3)  # want 3 runs per config
saver = get_csv_saver(root_dir="slune_results")

# Tell the searcher to use saver.exists(...) when iterating
searcher.check_existing_runs(saver)

for cfg in searcher:
    # If, for this cfg, saver.exists(cfg) returned 2, it will only yield one more run.
    # If exists >= runs, the config is skipped entirely.
    print("Next config to run:", cfg)
```

Notes:
- If you want skipping, set `runs > 0` and call `check_existing_runs(saver)` before iterating.
- Without a Saver, every configuration yields exactly `runs` times (or once if `runs=0`).