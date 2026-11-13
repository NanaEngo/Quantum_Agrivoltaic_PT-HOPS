#!/usr/bin/env python
"""Non-dyadic absorption spectra of the NPoM-dressed FMO complex (MesoHOPS 1.8).

Predicted observable for the Solar Energy V2611 package: linear absorption
fingerprints of the quantum channel, NPoM OFF vs ON, whose cavity-shifted
lines are falsifiable by 2DES/linear absorption at 295 K.

Conventions mirror the production framework exactly:
- units cm^-1 with fs times, T = 295 K, lambda_D = 35 cm^-1, gamma_D = 50 cm^-1,
  K = 2 Matsubara terms, the 12-mode Kleinekathofer/Coker vibronic ladder,
  hierarchy modes unbundled (the 1.8 spectroscopy path needs plain HOPS,
  so no SBD here; production data stay pinned to 1.7.0 + SBD=3).
- Hamiltonian centered by its diagonal mean (numerical hygiene, as in
  hops_simulator._init_mesohops); the mean is added back on the frequency
  axis so spectra read in absolute cm^-1 transition energies.
- NPoM ON: 9x9 dressing with plasmon on the zero of the site-energy axis,
  coupled to PLASMON_COUPLING_SITES with g0 = 120*sqrt(1/V), V = 0.8 nm^3
  (production reference), per diagnostics.NpomCoupling.
- Transition dipoles: equal collinear site dipoles (x-direction); the plasmon
  entry is optically bright under the same assumption. This is the stated
  assumption of the SM section, not a fitted choice.

Run (probe, ~1 trajectory, 40 fs):
    conda run -n MesoHOP-sim-18 python scripts/spectro_npom_fmo.py --probe
Run (production of the SM figure, N seeds per config, parallel):
    conda run -n MesoHOP-sim-18 python scripts/spectro_npom_fmo.py --full
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp

REPO = Path(__file__).resolve().parents[2]
P2 = REPO / "Redac_Paper2"
OUT_DIR = P2 / "data" / "spectro"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


p2c = _load(P2 / "src" / "constants.py", "p2_constants")
fwc = _load(REPO / "quantum_simulations_framework" / "src" / "core" / "constants.py", "fw_constants")

from mesohops.trajectory.hops_trajectory import HopsTrajectory as HOPS  # noqa: E402
from mesohops.util.bath_corr_functions import (  # noqa: E402
    bcf_convert_bo_to_exp,
    bcf_convert_dl_to_exp,
)
from mesohops.util.nondyadic_spectroscopy import calc_absorption_response  # noqa: E402


def fmo_hamiltonian() -> np.ndarray:
    h = np.diag(np.asarray(p2c.FMO_SITE_ENERGIES_CM, dtype=float)).astype(complex)
    for (i, j), v in p2c.FMO_COUPLINGS_CM.items():
        h[i, j] = h[j, i] = v
    return h


def dressed_hamiltonian(h_fmo: np.ndarray) -> np.ndarray:
    """NPoM dressing per diagnostics.NpomCoupling at the production reference volume."""
    g0 = float(p2c.NPoM_REFERENCE_COUPLING_CM * np.sqrt(p2c.NPoM_REFERENCE_MODE_VOLUME_NM3 / 0.8))
    n = h_fmo.shape[0]
    h = np.zeros((n + 1, n + 1), dtype=complex)
    h[:n, :n] = h_fmo
    for site in p2c.PLASMON_COUPLING_SITES:
        h[site, n] = h[n, site] = g0
    return h, g0


def eigen_fingerprint(h_off: np.ndarray, h_on: np.ndarray) -> None:
    """Dressed-Hamiltonian line positions (no propagator): single-excitation
    eigenvalues plus collinear-dipole oscillator strengths |sum_k c_k|^2.
    Exact for the coherent Hamiltonian; bath broadening/shifts would need the
    open-system propagator (future work). Energies referred to BChl a Qy."""
    qy_ref = 12500.0
    lines = {}
    for cfg, h in (("off", h_off), ("on", h_on)):
        w, v = np.linalg.eigh(h)
        energy = w.real + qy_ref
        strength = np.abs(v.sum(axis=0)) ** 2
        np.savetxt(
            OUT_DIR / f"spectrum_{cfg}.csv",
            np.column_stack([energy, strength]),
            delimiter=",",
        )
        top = sorted(np.argsort(strength)[::-1][:8], key=lambda i: energy[i])
        lines[cfg] = [[float(energy[i]), float(strength[i])] for i in top]
    pairs = []
    for a_on, s_on in lines["on"]:
        best = min(lines["off"], key=lambda t: abs(t[0] - a_on))
        if abs(best[0] - a_on) <= 250.0:
            pairs.append({"on_cm1": a_on, "off_cm1": best[0], "delta_cm1": a_on - best[0], "on_amp": s_on})
    payload = {"off": {"peaks": lines["off"]}, "on": {"peaks": lines["on"]}, "shift_table": pairs}
    (OUT_DIR / "peaks.json").write_text(json.dumps(payload, indent=2))
    print(f"[eigen] {len(pairs)} matched OFF->ON line shifts")
    for p in pairs:
        print(f"    {p['off_cm1']:.1f} -> {p['on_cm1']:.1f}  (delta {p['delta_cm1']:+.1f})")


def build_system_param(h: np.ndarray) -> tuple[dict, float]:
    """Embed the ground state as basis slot 0 (vector+NONLINEAR absorption in
    MesoHOPS 1.8 requires the 'embedded' Hilbert convention: NSTATES = n+1)."""
    n_sites = h.shape[0]
    n_emb = n_sites + 1
    l_ops = []
    for i in range(n_sites):
        op = np.zeros((n_emb, n_emb), dtype=complex)
        op[i + 1, i + 1] = 1.0
        l_ops.append(sp.csc_matrix(op))

    e_mean = float(np.mean(np.diag(h).real))
    h_shifted = h - e_mean * np.eye(n_sites, dtype=complex)
    h_emb = np.zeros((n_emb, n_emb), dtype=complex)
    h_emb[1:, 1:] = h_shifted  # ground slot at zero energy (reference point)

    dl_flat = bcf_convert_dl_to_exp(
        fwc.DEFAULT_REORGANIZATION_ENERGY,
        fwc.DEFAULT_DRUDE_CUTOFF,
        fwc.DEFAULT_TEMPERATURE,
        k_matsubara=p2c.K_MATSUBARA,
    )
    dl_pairs = [[dl_flat[i], dl_flat[i + 1]] for i in range(0, len(dl_flat), 2)]

    gw: list = []
    l_hier: list = []
    l_noise: list = []
    param_noise: list = []
    for i in range(n_sites):
        for g, w in dl_pairs:
            gw.append([g, w])
            l_hier.append(l_ops[i])
            l_noise.append(l_ops[i])
            param_noise.append([g, w])

    damp_raw = fwc.DEFAULT_VIBRONIC_DAMPING
    damp = (
        np.full(len(fwc.DEFAULT_VIBRONIC_FREQUENCIES), float(damp_raw))
        if np.isscalar(damp_raw)
        else np.asarray(damp_raw, dtype=float)
    )
    for freq, hr, d in zip(
        fwc.DEFAULT_VIBRONIC_FREQUENCIES, fwc.DEFAULT_HUANG_RHYS_FACTORS, damp, strict=False
    ):
        lambda_vib = hr * freq
        try:
            ud_flat = bcf_convert_bo_to_exp(
                lambda_vib, d, freq, fwc.DEFAULT_TEMPERATURE, k_matsubara=0
            )
            ud_pairs = [[ud_flat[i], ud_flat[i + 1]] for i in range(0, len(ud_flat), 2)]
        except Exception:
            ud_pairs = [[lambda_vib, freq + 1j * d]]
        for g, w in ud_pairs:
            for i in range(n_sites):
                gw.append([g, w])
                l_hier.append(l_ops[i])
                l_noise.append(l_ops[i])
                param_noise.append([g, w])

    def alpha_noise1(t_axis, g, w):
        return g * np.exp(-w * np.asarray(t_axis))

    system_param = {
        "HAMILTONIAN": h_emb,
        "GW_SYSBATH": gw,
        "L_HIER": l_hier,
        "L_NOISE1": l_noise,
        "ALPHA_NOISE1": alpha_noise1,
        "PARAM_NOISE1": param_noise,
    }
    return system_param, e_mean


def run_one(args: tuple) -> tuple:
    config, seed, t_max, t_step, maxhier = args
    h = fmo_hamiltonian()
    if config == "off":
        sys_h = h
    else:
        sys_h, _ = dressed_hamiltonian(h)
    system_param, _ = build_system_param(sys_h)
    n_sites = sys_h.shape[0]
    dipoles = np.zeros((n_sites, 3))
    dipoles[:, 0] = 1.0
    e1 = np.array([1.0, 0.0, 0.0])

    traj = HOPS(
        system_param,
        noise_param={
            "SEED": seed,
            "MODEL": "FFT_FILTER",
            "TLEN": float(t_max + 20.0),
            "TAU": t_step / 2.0,
        },
        hierarchy_param={"MAXHIER": maxhier},
        eom_param={"EQUATION_OF_MOTION": "NONLINEAR"},
    )
    traj.make_adaptive(delta_a=1e-3, delta_s=1e-3, update_step=50)
    t0 = time.time()
    c1 = np.asarray(calc_absorption_response(traj, dipoles, e1, t_max=t_max, t_step=t_step))
    return config, seed, c1, time.time() - t0


def spectrum(c1: np.ndarray, t_step: float, e_mean: float):
    """DC-removed, Hann-windowed power spectrum in absolute cm^-1 (grid step t_step..t_max)."""
    n = len(c1)
    c = c1 - c1.mean()
    c = c * np.hanning(n)
    spec = np.fft.fft(c)
    freqs = np.fft.fftfreq(n, d=t_step) * 2.0 * np.pi  # rad/fs
    pos = freqs > 0
    axis = freqs[pos] * 1e15 / (2.0 * np.pi * 2.99792458e10) + e_mean
    power = np.abs(spec[pos])
    return axis, power


def find_peaks(axis, power, frac=0.15, window=(50.0, 2500.0), max_peaks=6):
    p = power.copy()
    m = (axis < window[0]) | (axis > window[1])
    p[m] = 0.0
    thr = frac * p.max()
    peaks = []
    for i in range(2, len(p) - 2):
        if p[i] > thr and p[i] >= p[i - 1] and p[i] > p[i + 1] and p[i] > p[i - 2] and p[i] > p[i + 2]:
            peaks.append((float(axis[i]), float(power[i])))
            p[i] = 0.0
    return sorted(peaks, key=lambda t: -t[1])[:max_peaks]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="1 trajectory, 40 fs, OFF only (timing)")
    ap.add_argument("--full", action="store_true", help="N seeds per config at production depth")
    ap.add_argument("--n-seeds", type=int, default=6)
    ap.add_argument("--t-max", type=float, default=600.0)
    ap.add_argument("--t-step", type=float, default=0.5)
    ap.add_argument("--maxhier", type=int, default=8)
    ap.add_argument("--maxprocs", type=int, default=8)
    ap.add_argument("--summarize", action="store_true", help="skip jobs; FFT existing C1_*.csv on disk")
    ap.add_argument("--eigen", action="store_true", help="no propagator: dressed-Hamiltonian line positions")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jobs = []
    if args.probe:
        jobs = [("off", 101, 40.0, args.t_step, args.maxhier)]
    else:
        for cfg in ("off", "on"):
            for s in range(101, 101 + args.n_seeds):
                jobs.append((cfg, s, args.t_max, args.t_step, args.maxhier))

    print(f"[spectro] {len(jobs)} jobs, maxhier={args.maxhier}, t_step={args.t_step} fs")
    h_off = fmo_hamiltonian()
    _, e_mean_off = build_system_param(h_off)
    h_on, g0 = dressed_hamiltonian(h_off)
    _, e_mean_on = build_system_param(h_on)
    print(f"[spectro] g0={g0:.1f} cm^-1 | e_mean off/on = {e_mean_off:.1f}/{e_mean_on:.1f} cm^-1")

    if args.eigen:
        eigen_fingerprint(h_off, h_on)
        return

    if args.summarize:
        summarize(args.t_step, e_mean_off, e_mean_on)
        return

    t0 = time.time()
    if len(jobs) == 1:
        results_iter = iter([run_one(jobs[0])])
    else:
        ctx = mp.get_context("fork")
        with ctx.Pool(processes=min(len(jobs), args.maxprocs)) as pool:
            results_iter = pool.imap_unordered(run_one, jobs)
    for config, seed, c1, dt in results_iter:
        np.savetxt(OUT_DIR / f"C1_{config}_{seed}.csv", np.asarray(c1), delimiter=",")
        print(f"  {config} seed={seed}: len={len(c1)} traj_time={dt:.0f}s", flush=True)
    print(f"[spectro] wall time {time.time() - t0:.0f} s")

    if args.probe:
        print("[spectro] PROBE DONE")
        return

    summarize(args.t_step, e_mean_off, e_mean_on)


def summarize(t_step: float, e_mean_off: float, e_mean_on: float) -> None:
    """Average C1 traces found on disk (whatever completed), FFT, find peaks."""
    by_cfg: dict[str, list] = {}
    for path in sorted(OUT_DIR.glob("C1_*.csv")):
        config = path.stem.split("_")[1]
        by_cfg.setdefault(config, []).append(np.loadtxt(path, delimiter=","))
    print("[summarize] seeds on disk: " + ", ".join(f"{k}:{len(v)}" for k, v in sorted(by_cfg.items())))

    summary = {}
    for config, c1s in by_cfg.items():
        c = np.mean(c1s, axis=0)
        e_mean = e_mean_off if config == "off" else e_mean_on
        axis, power = spectrum(c, t_step, e_mean)
        np.savetxt(OUT_DIR / f"spectrum_{config}.csv", np.column_stack([axis, power]), delimiter=",")
        peaks = find_peaks(axis, power)
        summary[config] = {"axis": [axis.tolist(), power.tolist()], "peaks": peaks}
        print(f"  [{config}] top peaks (cm^-1): " + ", ".join(f"{a:.1f}({v:.2f})" for a, v in peaks))

    if "off" in summary and "on" in summary:
        pairs = []
        for (a_on, v_on) in summary["on"]["peaks"]:
            best = min(summary["off"]["peaks"], key=lambda t: abs(t[0] - a_on), default=None)
            if best is not None and abs(best[0] - a_on) < 60.0:
                pairs.append({"on_cm1": a_on, "off_cm1": best[0], "delta_cm1": a_on - best[0], "on_amp": v_on})
        summary["shift_table"] = pairs
        print("  [shift] OFF->ON matched line shifts (cm^-1):")
        for p in pairs:
            print(f"    {p['off_cm1']:.1f} -> {p['on_cm1']:.1f}  (Δ {p['delta_cm1']:+.1f})")

    slim = dict(summary)
    for cfg in ("off", "on"):
        if cfg in slim:
            slim[cfg].pop("axis", None)
    (OUT_DIR / "peaks.json").write_text(json.dumps(slim, indent=2, default=str))
    print("[spectro] DONE ->", OUT_DIR)


if __name__ == "__main__":
    main()
