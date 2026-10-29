"""BPSK symbol-timing recovery: Gardner PLL vs Gardner-measurement Kalman tracker.

Run: python timing_recovery_comparison.py [--quick]
Outputs CSV/JSON summary and PNG figures in ./results.
Requires numpy, scipy, matplotlib.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import fftconvolve


@dataclass
class Config:
    sps: int = 8
    n_symbols: int = 5000
    beta: float = 0.35
    span: int = 10
    loop_bw: float = 0.018
    damping: float = 0.707
    kf_phase_q: float = 2e-5
    kf_rate_q: float = 2e-8
    seed: int = 20261029


def rrc_taps(beta: float, span: int, sps: int) -> np.ndarray:
    """Unit-energy root-raised-cosine impulse response."""
    t = np.arange(-span * sps / 2, span * sps / 2 + 1) / sps
    h = np.zeros_like(t, dtype=float)
    for i, ti in enumerate(t):
        if abs(ti) < 1e-12:
            h[i] = 1 + beta * (4 / np.pi - 1)
        elif beta and abs(abs(4 * beta * ti) - 1) < 1e-10:
            h[i] = beta / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * ti * (1 - beta)) + 4 * beta * ti * np.cos(np.pi * ti * (1 + beta))) / (np.pi * ti * (1 - (4 * beta * ti) ** 2))
    return h / np.sqrt(np.sum(h * h))


def make_waveform(bits: np.ndarray, cfg: Config, ppm: float, offset: float, ebn0_db: float, rng: np.random.Generator):
    symbols = 2 * bits.astype(float) - 1
    up = np.zeros(len(symbols) * cfg.sps)
    up[::cfg.sps] = symbols
    h = rrc_taps(cfg.beta, cfg.span, cfg.sps)
    tx = fftconvolve(up, h, mode="full")
    # Receiver sampling clock is slightly different. Resample the continuous-time
    # transmit waveform onto its clock grid, preserving initial timing offset.
    n = np.arange(len(tx), dtype=float)
    query = n * (1.0 + ppm * 1e-6) + offset * cfg.sps
    impaired = np.interp(query, n, tx, left=0.0, right=0.0)
    # Real passband-equivalent baseband BPSK AWGN. Unit-energy symbols imply
    # variance N0/2 = 1/(2 Eb/N0) at the matched-filter input sample grid.
    gamma = 10 ** (ebn0_db / 10)
    impaired += rng.normal(0, np.sqrt(1 / (2 * gamma)), len(impaired))
    mf = fftconvolve(impaired, h, mode="full")
    delay = len(h) - 1
    return mf, delay


def interp(x: np.ndarray, t: float) -> float:
    i = int(np.floor(t))
    if i < 0 or i + 1 >= len(x):
        return 0.0
    f = t - i
    return float(x[i] * (1 - f) + x[i + 1] * f)


def run_loop(x: np.ndarray, delay: int, cfg: Config, method: str, initial_phase: float = 0.0,
             clock_ppm: float = 0.0, initial_offset_ui: float = 0.0):
    # Timing phase is represented in input samples; positive phase means later.
    # Gardner measurement e=(previous-current)*mid has local slope < 0 for this
    # convention, so phase correction is -e/slope.
    bw, zeta = cfg.loop_bw, cfg.damping
    theta = bw / (zeta + 0.25 / zeta)
    denom = 1 + 2 * zeta * theta + theta * theta
    alpha = 4 * zeta * theta / denom
    beta = 4 * theta * theta / denom
    t = delay + cfg.sps + initial_phase * cfg.sps
    omega = float(cfg.sps)
    errors, phases, samples, times = [], [], [], []
    # KF state [phase(samples), rate(samples/symbol)]; measurement is phase error.
    state = np.array([0.0, 0.0])
    P = np.diag([0.25, 1e-4])
    F = np.array([[1.0, 1.0], [0.0, 1.0]])
    H = np.array([[1.0, 0.0]])
    Q = np.diag([cfg.kf_phase_q, cfg.kf_rate_q])
    R = 0.015
    prev = None
    for k in range(2, cfg.n_symbols - 2):
        if method == "gardner":
            t += omega
        else:
            state = F @ state
            P = F @ P @ F.T + Q
            t += omega + state[1]
        early = interp(x, t - cfg.sps / 2)
        on = interp(x, t)
        late = interp(x, t + cfg.sps / 2)
        if prev is not None:
            e = (prev - on) * interp(x, t - cfg.sps / 2)
            # Normalize for signal level, stabilizing gains across SNR.
            e /= max(0.1, (prev * prev + on * on + 1e-8))
            if method == "gardner":
                omega += beta * e
                omega = float(np.clip(omega, cfg.sps * 0.98, cfg.sps * 1.02))
                t += alpha * e
            else:
                # Calibrate TED gain by a local linear approximation. For the
                # error definition above, increasing sampling time decreases e.
                # Using measured innovation as phase pseudo-measurement.
                z = np.clip(e * 0.35, -0.45, 0.45)
                innovation = z - float((H @ state).item())
                S = float((H @ P @ H.T).item() + R)
                K = (P @ H.T / S).reshape(2)
                state += K * innovation
                P = (np.eye(2) - np.outer(K, H.reshape(2))) @ P
                state[0] = float(np.clip(state[0], -cfg.sps / 2, cfg.sps / 2))
                state[1] = float(np.clip(state[1], -0.03, 0.03))
                t += 0.35 * state[0]
            errors.append(e)
        prev = on
        samples.append(on)
        ideal_receiver_epoch = (delay + k * cfg.sps - initial_offset_ui * cfg.sps) / (1 + clock_ppm * 1e-6)
        phases.append((t - ideal_receiver_epoch) / cfg.sps)
        times.append(k)
    return np.asarray(samples), np.asarray(errors), np.asarray(phases), np.asarray(times)


def align_metrics(samples, bits, times, cfg):
    # Remove fixed matched-filter delay; loop runs on symbol epochs k.
    valid = (times >= cfg.span) & (times < len(bits) - cfg.span)
    ix = times[valid].astype(int)
    y = samples[valid]
    b = bits[ix]
    # Resolve BPSK's inherent 180-degree ambiguity by choosing better polarity.
    hard = (y >= 0).astype(int)
    if np.mean(hard == b) < 0.5:
        hard = 1 - hard
    return b, hard, y


def ber_stats(bits, hard):
    errors = int(np.count_nonzero(bits != hard))
    return errors, errors / max(1, len(bits))


def one_trial(cfg, snr, ppm, offset, seed, method):
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, cfg.n_symbols)
    x, delay = make_waveform(bits, cfg, ppm, offset, snr, rng)
    syms, err, phase, times = run_loop(x, delay, cfg, method, initial_phase=0.0,
                                      clock_ppm=ppm, initial_offset_ui=offset)
    b, hard, _ = align_metrics(syms, bits, times, cfg)
    nerr, ber = ber_stats(b, hard)
    tail = phase[int(0.65 * len(phase)):]
    # estimate residual timing jitter around the known phase trajectory;
    # ppm drift is tracked separately as rate error.
    jitter = float(np.std(tail - np.mean(tail))) if len(tail) else float("nan")
    threshold = 0.05
    inside = np.abs(phase) < threshold
    lock_symbols = cfg.n_symbols
    for start in range(max(0, len(inside) - 99)):
        if np.all(inside[start:start + 100]):
            lock_symbols = int(times[start])
            break
    return {"ber": ber, "bit_errors": nerr, "timing_jitter_ui": jitter, "lock_symbols": lock_symbols,
            "phase": phase, "error": err, "times": times, "bits": b, "hard": hard}


def s_curve(cfg, method="gardner", snr=30):
    phases = np.linspace(-0.5, 0.5, 101, endpoint=True)
    values = []
    for i, phase in enumerate(phases):
        rng = np.random.default_rng(cfg.seed + i)
        bits = np.tile([0, 1], cfg.n_symbols // 2 + 1)[:cfg.n_symbols]
        x, delay = make_waveform(bits, cfg, 0, phase, snr, rng)
        # Open-loop TED average at fixed phase: use symbol/midpoint samples.
        base = delay
        es = []
        for k in range(cfg.span + 2, cfg.n_symbols - cfg.span - 2):
            t = base + k * cfg.sps
            prev = interp(x, t - cfg.sps)
            curr = interp(x, t)
            mid = interp(x, t - cfg.sps / 2)
            es.append((prev - curr) * mid)
        values.append(np.mean(es))
    return phases, np.asarray(values)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true", help="short run for a fast smoke check")
    ap.add_argument("--trials", type=int, default=None, help="Monte Carlo trials per scenario")
    args = ap.parse_args()
    cfg = Config(n_symbols=1200 if args.quick else 5000)
    trials = args.trials or (2 if args.quick else 8)
    out = Path("results")
    out.mkdir(exist_ok=True)
    methods = ["gardner", "kalman"]
    scenarios = [(snr, ppm, off) for snr, ppm, off in [(0, 0, 0.35), (4, 0, -0.4), (8, 100, 0.3), (12, -100, -0.25), (18, 250, 0.45)]]
    rows, traces = [], {}
    for si, (snr, ppm, off) in enumerate(scenarios):
        for method in methods:
            results = [one_trial(cfg, snr, ppm, off, cfg.seed + si * 1000 + tr, method) for tr in range(trials)]
            rows.append({"method": method, "ebn0_db": snr, "clock_offset_ppm": ppm, "initial_offset_ui": off,
                         "trials": trials, "mean_ber": float(np.mean([r["ber"] for r in results])),
                         "mean_timing_jitter_ui": float(np.mean([r["timing_jitter_ui"] for r in results])),
                         "mean_lock_symbols": float(np.mean([r["lock_symbols"] for r in results])),
                         "mean_bit_errors": float(np.mean([r["bit_errors"] for r in results]))})
            if si == 2:
                traces[method] = results[0]
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    with (out / "config.json").open("w", encoding="utf-8") as f:
        json.dump({"config": asdict(cfg), "trials_per_scenario": trials, "scenarios": scenarios,
                   "note": "Illustrative baseband AWGN simulation; compare timing algorithms under identical waveforms."}, f, indent=2)

    # S-curve, BER and residual timing jitter summaries.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ph, curve = s_curve(cfg)
    ax.plot(ph, curve, color="navy"); ax.axhline(0, color="black", lw=.8); ax.axvline(0, color="gray", ls="--")
    ax.set(title="Open-loop Gardner TED S-curve", xlabel="Timing phase error (UI)", ylabel="Mean TED output")
    ax.grid(True, alpha=.3); fig.tight_layout(); fig.savefig(out / "s_curve.png", dpi=160); plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.3))
    labels = [f"{s} dB\n{p:+} ppm" for s, p, _ in scenarios]
    for method in methods:
        rr = [r for r in rows if r["method"] == method]
        axs[0].semilogy(range(len(rr)), [max(r["mean_ber"], 1e-5) for r in rr], "o-", label=method.title())
        axs[1].plot(range(len(rr)), [r["mean_timing_jitter_ui"] for r in rr], "o-", label=method.title())
    axs[0].set(title="BER by channel condition", ylabel="BER", xticks=range(len(labels)), xticklabels=labels)
    axs[1].set(title="Residual timing jitter", ylabel="Standard deviation (UI)", xticks=range(len(labels)), xticklabels=labels)
    for ax in axs: ax.grid(True, which="both", alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(out / "comparison.png", dpi=160); plt.close(fig)

    fig, axs = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    for method, data in traces.items():
        axs[0].plot(data["times"], data["phase"], lw=.8, label=method.title())
        axs[1].plot(data["times"][:len(data["error"])], data["error"], lw=.6, alpha=.8, label=method.title())
    axs[0].set(ylabel="Timing phase error (UI)", title="Representative tracking trace (8 dB, +100 ppm)")
    axs[1].set(xlabel="Symbol index", ylabel="Normalized TED error")
    for ax in axs: ax.grid(True, alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(out / "tracking_trace.png", dpi=160); plt.close(fig)

    print("Symbol timing recovery comparison")
    print(f"Symbols/trial: {cfg.n_symbols}; Monte Carlo trials/scenario: {trials}; roll-off: {cfg.beta}; samples/symbol: {cfg.sps}")
    print("method   Eb/N0  ppm  BER         jitter(UI)  lock(symbols)")
    for r in rows:
        print(f"{r['method']:<8} {r['ebn0_db']:>4} {r['clock_offset_ppm']:>5} {r['mean_ber']:<11.4g} {r['mean_timing_jitter_ui']:<11.4g} {r['mean_lock_symbols']:.1f}")
    print(f"\nWrote {out / 'summary.csv'}, {out / 'config.json'}, and PNG plots to {out.resolve()}")


if __name__ == "__main__":
    main()
