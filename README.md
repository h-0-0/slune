# Slune: Simple SLURM-based Experiment Launcher 🚀

[![PyPI version](https://img.shields.io/pypi/v/slune-lib.svg)](https://pypi.org/project/slune-lib)
[![Python Version](https://img.shields.io/pypi/pyversions/slune-lib.svg)](https://pypi.org/project/slune-lib)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

Slune ( **Sl**urm + t**une** ) is a zero-boilerplate helper library for launching embarrassingly-parallel jobs—such as hyper-parameter searches—on a SLURM cluster.

* ⚡ **Fast turnaround** – split large searches into many tiny jobs and let the scheduler run them as soon as resources are free.
* 🪄 **Simple** – a tiny API surface; one import gives you everything you need.
* 🔧 **Flexible** – minimal assumptions about your project; works with any executable script.
* 📑 **Organised results** – pluggable ‘Saver’ implementations (CSV by default) keep your experiments tidy and queryable.

The goal is to stay *bloat-free*: every helper is fully optional and easy to read or extend.

---

## Installation

Stable release:

```bash
pip install slune-lib
```

Bleeding-edge (main branch):

```bash
pip install "git+https://github.com/h-0-0/slune.git#egg=slune-lib"
```

Requires Python 3.8+ and access to an `sbatch` command (a SLURM installation or simulator).

---

## Quick start

1.  Define the search space.
2.  Submit jobs with a single function call.
3.  Read the results when the jobs finish.

```python
from slune import SearcherGrid, sbatchit, get_csv_saver

# 1️⃣  Search space: try three values of `alpha`
searcher = SearcherGrid({'alpha': [0.25, 0.5, 0.75]}, runs=1)

# 2️⃣  Submit jobs
sbatchit(
    script_path="model.py",      # training script that consumes --alpha argument
    sbatch_path="template.sh",   # SBATCH template containing your cluster directives
    searcher=searcher,
    cargs={},                    # constant args shared by every job
    saver=None                   # optional SaverCsv; skip to rerun all jobs
)

# 3️⃣  Retrieve best result
saver = get_csv_saver()
params, mse = saver.read(params=[], metric_name="mse", select_by="min")
print("Best parameters:", params, "MSE:", mse)
```

The `examples/` directory contains full notebooks that walk through multi-node experiments.

---

## Documentation

Full API reference and guides are hosted at:

👉  https://h-0-0.github.io/slune/

---

## Feature overview

* `SearcherGrid` – Cartesian product grid search (more search strategies coming soon)
* `SaverCsv` + `LoggerDefault` – hierarchical CSV logging out-of-the-box
* Helper utilities: `lsargs`, `dict_to_strings`, filesystem helpers and more
* Works with *any* language—you can pass parameters to a Bash, R or Julia script just as easily

---

## Roadmap

* Enhanced SLURM integration: smarter job names, output paths, notifications
* Random / Bayesian / cross-validation search strategies
* Additional saving back-ends (TensorBoard, database, single-CSV)
* CLI tools for monitoring, resubmitting and cancelling jobs
* Language-agnostic templates for non-Python pipelines

Have an idea? Open an issue or PR ✨

---

## Contributing

1. Fork the repo and create a feature branch.
2. Run the test suite (`pytest`).
3. Open a Pull Request describing your changes.

See `CONTRIBUTING.md` for more details.

---

## License

Licensed under the MIT License – see the `LICENSE` file for details.