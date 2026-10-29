# Evaluation measures

The results report three measures for each method and channel scenario:

- **Bit error rate (BER):** hard-decision bit errors divided by scored bits.
  BPSK polarity ambiguity is resolved for scoring by selecting the better of
  the two possible polarities.
- **Residual timing jitter:** standard deviation of timing phase error in unit
  intervals (UI) over the final 35% of a burst.
- **Lock time:** first symbol after which absolute timing error remains below
  0.05 UI for 100 consecutive symbols. A trial that never meets this condition
  is censored at the burst length.

BER includes acquisition symbols, so a longer acquisition period can affect
the measured BER. A plotted zero-error scenario is a finite-run observation,
not evidence of a true zero BER. See the CSV and chart notes for the display
floor used for zero-error points.
