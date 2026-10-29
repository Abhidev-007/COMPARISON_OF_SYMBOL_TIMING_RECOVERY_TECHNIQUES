# Kalman-based timing tracker

The comparison uses the same Gardner timing-error detector for both methods.
The Kalman branch therefore compares a model-based loop update with the
Gardner proportional-integral update; it is not an independent detector.

The filter state is `[timing phase, sampling-rate error]`. A constant-rate
state transition predicts phase drift, and a scalar timing-phase
pseudo-measurement derived from the Gardner error corrects the prediction.
The process covariance controls expected state changes and the measurement
covariance controls trust in each detector observation.

This is an illustrative linearized tracker. Its state model and noise
covariances are fixed in the current run, and should be calibrated before use
in a modem or hardware receiver. See `docs/references.md` for background.
