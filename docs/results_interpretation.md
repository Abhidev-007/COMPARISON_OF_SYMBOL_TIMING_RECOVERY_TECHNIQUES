# Reading the included results

`results/comparison.png` plots BER and residual timing jitter against the
tested channel cases. `results/tracking_trace.png` shows one representative
run; aggregate values across trials are in `results/summary.csv`.

In the included run, the Kalman tracker has lower mean jitter and shorter mean
lock time in the five listed scenarios. Its BER is lower in several low- and
mid-SNR cases, while both methods record no observed errors in the 12 dB
finite run. These findings describe this waveform model, detector
linearization, fixed tuning, and limited seed set only. They do not establish
general superiority across receivers or parameter choices.

The open-loop S-curve in `results/s_curve.png` is a detector diagnostic. It
shows mean Gardner error versus timing phase, not closed-loop lock behavior.
