# Figure guide

- **comparison.png:** mean BER and residual timing jitter by channel scenario.
  BER uses a `10^-5` plotting floor so zero observed errors remain visible.
- **s_curve.png:** open-loop mean Gardner detector output across timing phase.
  The zero crossing and local slope help check detector convention and sign.
- **tracking_trace.png:** one representative 8 dB, +100 ppm, +0.30 UI trial.
  It plots phase error and normalized detector error over the burst.

For exact aggregate values and scenario metadata, use `summary.csv` and
`config.json` rather than estimating values from the rendered figures.
