# Comparison of Symbol Timing Recovery Techniques

This repository contains a BPSK communications project and a reproducible
Python comparison of two symbol-timing trackers: a Gardner timing loop and a
Kalman-based tracker driven by the same Gardner timing-error detector.

The timing study models BPSK mapping, root-raised-cosine pulse shaping,
fractional timing offset, sampling-clock mismatch, AWGN, matched filtering,
timing recovery, and hard-decision scoring. Its code and results are limited to
this symbol-timing comparison.

The simulation is a focused software experiment; it does not claim to model
the complete packet receiver or real-time DSP hardware.

## Run the timing comparison

Install dependencies and run from the repository root:

```console
python -m pip install -r requirements.txt
python timing_recovery_comparison.py
```

Use `--quick` for a smaller run or `--trials N` to set the Monte Carlo trials
per channel scenario. The program writes `results/summary.csv`,
`results/config.json`, and three PNG figures. The checked-in versions are the
default 5,000-symbol, eight-trial run.

## Evaluation and project notes

The reported measures are bit error rate, residual timing jitter in unit
intervals, and lock time in symbols. The result files and metric definitions
are documented in [`docs/`](docs/system_overview.md), including the
[Gardner method](docs/gardner_method.md),
[Kalman tracker](docs/kalman_method.md),
[test scenarios](docs/test_scenarios.md),
[results interpretation](docs/results_interpretation.md),
[limitations](docs/limitations.md),
[figure guide](docs/figures.md),
[reproducibility notes](docs/reproducibility.md), and
[research references](docs/references.md).
