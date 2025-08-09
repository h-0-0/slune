# Logger tutorial: LoggerDefault

Slune Loggers collect metrics during a run. `LoggerDefault` stores each call to `log({...})` as a new row in a pandas DataFrame at `logger.results`. The first column is a timestamp of when `log` was called.

## What it does
- Keeps an in-memory DataFrame of metrics for the current run
- Appends a timestamped row on every `log({...})`
- Offers `read_log(df, metric, select_by=...)` to select a value or series from a single run by:
  - `max`, `min`, `last`, `first`, `mean`, `median`, or `all`

## Quick start
```python
from slune.loggers.default import LoggerDefault

logger = LoggerDefault()

# Log metrics as you compute them
logger.log({"loss": 0.9, "acc": 0.40})
logger.log({"loss": 0.6, "acc": 0.60})
logger.log({"loss": 0.7, "acc": 0.55})

# Inspect current results for this run
print(logger.results)
```

## Selecting values from a run
Use `read_log` to select a value (or series with `all`) for a single metric inside one run’s DataFrame.
```python
# Highest accuracy observed in this run
best_acc = logger.read_log(logger.results, metric_name="acc", select_by="max")

# Lowest loss
min_loss = logger.read_log(logger.results, metric_name="loss", select_by="min")

# Last logged accuracy
last_acc = logger.read_log(logger.results, metric_name="acc", select_by="last")

# Entire series
acc_series = logger.read_log(logger.results, metric_name="acc", select_by="all")
```

Notes:
- `LoggerDefault` does not write to disk by itself. Pair it with a Saver (e.g., `SaverCsv`) to persist results.
- You generally won’t call `read_log` directly when using savers since they wrap the logger and provide higher-level `read(...)` across runs.