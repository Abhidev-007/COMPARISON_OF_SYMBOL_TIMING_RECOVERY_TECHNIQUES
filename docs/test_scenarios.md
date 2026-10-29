# Test scenarios

The stored default run uses 5,000 symbols per trial and eight Monte Carlo
trials per scenario. Both methods share each generated bit sequence, channel
condition, and random seed.

| Eb/N0 | Clock mismatch | Initial timing offset | Purpose |
|---:|---:|---:|---|
| 0 dB | 0 ppm | +0.35 UI | Low SNR |
| 4 dB | 0 ppm | −0.40 UI | Moderate SNR |
| 8 dB | +100 ppm | +0.30 UI | Noise and clock drift |
| 12 dB | −100 ppm | −0.25 UI | High SNR with drift |
| 18 dB | +250 ppm | +0.45 UI | Larger clock mismatch |

The complete parameters and exact scenario values are recorded in
`results/config.json`. This is a small comparison matrix, not an exhaustive
parameter sweep.
