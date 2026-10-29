# Gardner timing loop

The Gardner detector is a non-data-aided timing-error detector. It uses a
midpoint sample and adjacent symbol samples; for one common sign convention,

`e[k] = (y[k-1] - y[k]) y[k-1/2]`.

The detector error drives a second-order proportional-integral timing loop.
The proportional path adjusts the current sampling phase, while the integral
path updates the estimated samples per symbol. The project normalizes the
detector output and derives loop gains from the configured loop bandwidth and
damping factor.

The detector sign depends on sample and error conventions. The included
`results/s_curve.png` checks the mean detector response around the aligned
sampling phase for this implementation. Gardner's original paper is listed in
`docs/references.md`.
