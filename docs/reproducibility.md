# Reproducibility

The default seed, signal parameters, scenario matrix, and trial count are
saved in `results/config.json`. The summarized measurements are in
`results/summary.csv`; the accompanying figures are PNG files under `results/`.

From the repository root, install the listed Python dependencies and run:

```console
python timing_recovery_comparison.py
```

Use `--quick` for a smaller run or `--trials N` to select the Monte Carlo
trial count. The program writes updated CSV, JSON, and plot files to `results/`.
Numerical values may differ if the seed, parameters, library versions, or code
are changed.
