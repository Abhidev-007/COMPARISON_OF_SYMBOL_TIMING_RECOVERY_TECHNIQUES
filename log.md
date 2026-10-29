Work log

06-09-2026: 3hrs  Abhinand,Abhilash
- Research regarding techniques Forward error correction : Viterbi encoding and frame generation.
- Addition of channel noise AWGN and attenuation.
- Detailed mathematical analysis of Costas loop
- Work division between group members

14- 09-2026: Abhinand
- Set up git in local machine
- Setup a bitstream generator and BPSK mapper(Standard BPSK)

15 - 09 -26: Abhinand
- Built an RRC pulshe shaping filter from scratch

21-09-2006 Abhilash
- Created a function for encoding the payload and crc

- Added a reproducible Python simulation comparing a Gardner timing loop with a Kalman-based timing tracker.
- Evaluated both methods on shared BPSK waveforms across five SNR, timing-offset, and clock-mismatch scenarios.
- Recorded BER, residual timing jitter, and lock time in the results table.
- Generated the BER/jitter comparison, Gardner S-curve, and representative tracking-trace figures.
- Added method descriptions, research references, run instructions, metric definitions, and simulation limitations.
- Removed standalone bit-generation, FEC, and RRC demo files; the timing simulator contains its own BPSK/RRC chain and does not model FEC.
- Removed the evaluation folder because its BER examples use temporary placeholder values rather than timing-recovery results.
- Published the feature branch and merged its 21 documented commits into `main`.

29-10-2026: Repository cleanup

- Removed redundant project files that were outside the focused symbol-timing comparison.
- Updated the README and work log to describe the focused repository contents.
