# Scope and limitations

- The channel includes baseband AWGN, an initial fractional timing offset,
  and sampling-clock mismatch. It does not include multipath or fading.
- Timing interpolation is linear; a practical receiver may use a higher-order
  interpolator or polyphase filter bank.
- The Kalman tracker uses a linearized pseudo-measurement derived from the
  Gardner detector and illustrative fixed covariance values.
- The run has five scenarios and eight trials per scenario. More seeds,
  confidence intervals, and parameter sweeps are needed for stronger claims.
- There is no carrier recovery, preamble-based BPSK polarity resolver, FEC,
  packet framing, quantization, or real-time hardware profiling.
- The results are Python simulation outputs, not DSP-board measurements.

Future work can add Mueller–Müller or early-late timing detectors, multipath,
adaptive tuning, confidence intervals, and target-hardware profiling.
