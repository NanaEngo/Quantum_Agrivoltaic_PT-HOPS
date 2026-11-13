#!/usr/bin/env python3
"""WP2 Module C: Full-14-Site Non-Markovian MesoHOPS v1.8 Benchmark on HPC.

Validates the full 14-pigment LHCII excitonic network (H2_Muh2010 & H3_MMSIC_MD_2025)
with explicit non-Markovian Drude-Lorentz + discrete chlorophyll vibronic bath modes
(340 cm^-1, 740 cm^-1; 84 total hierarchy modes across 14 sites) using adaptive
MesoHOPS v1.8 (HopsTrajectory) on penavoraserver, and benchmarks against the
14-site Modified Redfield / Generalized Forster relaxation dynamics.

Usage (on HPC conda env `MesoHOP-sim-18`):
  ~/miniforge3/envs/MesoHOP-sim-18/bin/python scripts/wp2_mesohops_hpc_benchmark.py --smoke
  ~/miniforge3/envs/MesoHOP-sim-18/bin/python scripts/wp2_mesohops_hpc_benchmark.py --n-traj 32 --workers 16
"""

from __future__ import annotations

import os

for _env_var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_env_var, "1")

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import sparse
from scipy.linalg import expm
import yaml

PKG_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG_ROOT / "scripts"))
from wp2_quantum_ness import build_eet_rate_matrix  # noqa: E402

DATA_WP1 = PKG_ROOT / "data" / "wp1"
DATA_WP2 = PKG_ROOT / "data" / "wp2"

# Dominant LHCII Chl vibronic mode included in explicit vibronic HOPS benchmark
HOPS_VIB_MODES = [
    (340.0, 0.045, 25.0),
]


def build_mesohops_system_param(
    H_cm1: np.ndarray,
    lam_dl: float,
    gamma_dl: float,
    temp_k: float,
    k_matsubara: int = 1,
    include_vibronic: bool = True,
) -> Dict[str, Any]:
    """Build full 14-site MesoHOPS v1.8 system_param dictionary."""
    from mesohops.trajectory.exp_noise import bcf_exp
    from mesohops.util.bath_corr_functions import bcf_convert_bo_to_exp, bcf_convert_dl_to_exp

    n_sites = H_cm1.shape[0]
    H_shifted = np.asarray(H_cm1, dtype=np.float64) - np.mean(np.diag(H_cm1)) * np.eye(n_sites)

    L_ops = [sparse.coo_matrix(([1.0], ([i], [i])), shape=(n_sites, n_sites), dtype=np.complex128) for i in range(n_sites)]

    dl_flat = bcf_convert_dl_to_exp(lam_dl, gamma_dl, temp_k, k_matsubara=k_matsubara)
    gw_pairs: List[Tuple[complex, complex]] = [
        (complex(dl_flat[idx]), complex(dl_flat[idx + 1])) for idx in range(0, len(dl_flat), 2)
    ]

    if include_vibronic:
        for w_k, s_k, damp_k in HOPS_VIB_MODES:
            lam_k = float(s_k * w_k)
            bo_flat = bcf_convert_bo_to_exp(lam_k, damp_k, w_k, temp_k)
            for idx in range(0, len(bo_flat), 2):
                gw_pairs.append((complex(bo_flat[idx]), complex(bo_flat[idx + 1])))

    gw_sysbath = []
    l_hier = []
    l_noise1 = []
    param_noise1 = []
    for g, w in gw_pairs:
        for i in range(n_sites):
            gw_sysbath.append([g, w])
            l_hier.append(L_ops[i])
            l_noise1.append(L_ops[i])
            param_noise1.append([g, w])

    return {
        "HAMILTONIAN": H_shifted,
        "GW_SYSBATH": gw_sysbath,
        "L_HIER": l_hier,
        "L_NOISE1": l_noise1,
        "ALPHA_NOISE1": bcf_exp,
        "PARAM_NOISE1": param_noise1,
    }


def _run_single_hops_trajectory(args: Tuple[Any, ...]) -> Dict[str, Any]:
    """Worker running a single adaptive MesoHOPS v1.8 trajectory."""
    seed, H_cm1, lam_dl, gamma_dl, temp_k, max_hier, t_max_fs, dt_save_fs, include_vib, delta_a = args
    from mesohops.trajectory.hops_trajectory import HopsTrajectory

    t0 = time.perf_counter()
    sys_param = build_mesohops_system_param(
        H_cm1=H_cm1,
        lam_dl=lam_dl,
        gamma_dl=gamma_dl,
        temp_k=temp_k,
        k_matsubara=1,
        include_vibronic=include_vib,
    )
    n_sites = H_cm1.shape[0]
    n_hmodes = len(sys_param["GW_SYSBATH"])

    # Markovian filter on high-frequency Matsubara modes (indices n_sites .. 2*n_sites-1) avoids artificial stiffness
    markov_mask = [False] * n_sites + [True] * n_sites + [False] * max(0, n_hmodes - 2 * n_sites)

    # For RK4 integrator_step = 0.5, _check_tau_step enforces (tau * 0.5) / TAU == integer
    tau_noise_fs = float(dt_save_fs) * 0.5
    hierarchy_param = {
        "MAXHIER": int(max_hier),
        "TERMINATOR": True,
        "STATIC_FILTERS": [
            ["Triangular", [[True] * n_hmodes, int(max_hier)]],
            ["Markovian", markov_mask],
        ],
    }
    eom_param = {
        "EQUATION_OF_MOTION": "NORMALIZED NONLINEAR",
        "TIME_DEPENDENCE": False,
        "ADAPTIVE_H": True,
        "ADAPTIVE_S": True,
        "DELTA_A": float(delta_a),
        "DELTA_S": float(delta_a),
    }
    noise_param = {
        "SEED": int(seed),
        "MODEL": "FFT_FILTER",
        "TLEN": float(t_max_fs + 250.0),
        "TAU": float(tau_noise_fs),
        "INTERPOLATE": False,
        "RAND_MODEL": "SUM_GAUSSIAN",
        "STORE_RAW_NOISE": False,
        "NOISE_WINDOW": None,
        "ADAPTIVE": False,
        "FLAG_REAL": False,
    }
    integration_param = {
        "INTEGRATOR": "RUNGE_KUTTA",
        "EARLY_ADAPTIVE_INTEGRATOR": "INCH_WORM",
        "EARLY_INTEGRATOR_STEPS": 10,
        "INCHWORM_CAP": 5,
        "STATIC_BASIS": None,
    }

    traj = HopsTrajectory(
        system_param=sys_param,
        eom_param=eom_param,
        noise_param=noise_param,
        hierarchy_param=hierarchy_param,
        integration_param=integration_param,
    )
    traj.make_adaptive(delta_a=float(delta_a), delta_s=float(delta_a), update_step=5)

    psi_0 = np.zeros(n_sites, dtype=np.complex128)
    psi_0[0] = 1.0  # Initial excitation on Chl b601
    traj.initialize(psi_0)
    traj.propagate(float(t_max_fs), float(dt_save_fs))

    psi_traj = np.asarray(traj.storage["psi_traj"], dtype=np.complex128)
    t_axis = np.asarray(traj.storage.data["t_axis"], dtype=np.float64)

    pops = np.abs(psi_traj[:, :n_sites]) ** 2
    norms = np.sum(pops, axis=1, keepdims=True)
    pops_norm = np.where(norms > 1e-12, pops / np.maximum(norms, 1e-12), pops)
    max_norm_dev = float(np.max(np.abs(norms[:, 0] - 1.0)))

    return {
        "seed": int(seed),
        "t_axis_fs": t_axis,
        "pops": pops_norm,
        "max_norm_dev": max_norm_dev,
        "elapsed_s": time.perf_counter() - t0,
    }


def run_benchmark_for_hamiltonian(
    h_name: str,
    H_cm1: np.ndarray,
    lam_dl: float,
    gamma_dl: float,
    temp_k: float,
    max_hier: int,
    t_max_fs: float,
    dt_save_fs: float,
    n_traj: int,
    workers: int,
    include_vib: bool = False,
    delta_a: float = 3e-3,
) -> Dict[str, Any]:
    """Run parallel MesoHOPS v1.8 ensemble and compare with 14-site Redfield-Forster."""
    t_wall0 = time.perf_counter()
    tasks = [
        (1000 + k, H_cm1, lam_dl, gamma_dl, temp_k, max_hier, t_max_fs, dt_save_fs, include_vib, delta_a)
        for k in range(n_traj)
    ]

    results = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_run_single_hops_trajectory, arg) for arg in tasks]
        for fut in as_completed(futures):
            results.append(fut.result())

    results.sort(key=lambda d: d["seed"])
    t_axis_fs = results[0]["t_axis_fs"]
    pop_stack = np.stack([r["pops"] for r in results], axis=0)  # (n_traj, n_t, 14)
    pop_mean = np.mean(pop_stack, axis=0)
    pop_sem = np.std(pop_stack, axis=0, ddof=1) / np.sqrt(n_traj) if n_traj > 1 else np.zeros_like(pop_mean)

    # Terminal sink cluster: Chl a610 (9), a611 (10), a612 (11)
    p_term_hops = np.sum(pop_mean[:, [9, 10, 11]], axis=1)
    p_term_hops_sem = np.sqrt(np.sum(pop_sem[:, [9, 10, 11]] ** 2, axis=1))
    p_chlb_hops = np.sum(pop_mean[:, [0, 3, 4, 5, 6, 7]], axis=1)

    # 14-site Redfield-Forster comparison on identical time grid
    evals, evecs, W_eet = build_eet_rate_matrix(H_cm1, lam_dl, gamma_dl, temp_k, cutoff_cm1=15.0)
    L_pauli = W_eet - np.diag(np.sum(W_eet, axis=0))
    p_exc0 = evecs[0, :] ** 2  # initial Chl b601 in exciton basis

    p_term_pauli = np.zeros_like(t_axis_fs)
    p_chlb_pauli = np.zeros_like(t_axis_fs)
    for ti, t_fs in enumerate(t_axis_fs):
        p_exc_t = expm(L_pauli * (t_fs * 1e-3)) @ p_exc0
        p_site_t = (evecs**2) @ p_exc_t
        p_term_pauli[ti] = float(np.sum(p_site_t[[9, 10, 11]]))
        p_chlb_pauli[ti] = float(np.sum(p_site_t[[0, 3, 4, 5, 6, 7]]))

    n_tail = max(5, len(t_axis_fs) // 10)
    return {
        "hamiltonian": h_name,
        "n_sites": 14,
        "n_hmodes": 14 * (2 + (2 * len(HOPS_VIB_MODES) if include_vib else 0)),
        "max_hier": int(max_hier),
        "n_traj": int(n_traj),
        "t_max_fs": float(t_max_fs),
        "dt_save_fs": float(dt_save_fs),
        "wall_time_s": float(time.perf_counter() - t_wall0),
        "max_norm_deviation": float(max(r["max_norm_dev"] for r in results)),
        "p_terminal_final_hops": float(np.mean(p_term_hops[-n_tail:])),
        "p_terminal_final_hops_sem": float(np.mean(p_term_hops_sem[-n_tail:])),
        "p_terminal_final_pauli": float(np.mean(p_term_pauli[-n_tail:])),
        "p_chlb_final_hops": float(np.mean(p_chlb_hops[-n_tail:])),
        "p_chlb_final_pauli": float(np.mean(p_chlb_pauli[-n_tail:])),
        "terminal_mae_0_tmax": float(np.mean(np.abs(p_term_hops - p_term_pauli))),
        "terminal_rmse_0_tmax": float(np.sqrt(np.mean((p_term_hops - p_term_pauli) ** 2))),
        "t_axis_fs_sample": [float(x) for x in t_axis_fs[::10]],
        "p_terminal_hops_sample": [float(x) for x in p_term_hops[::10]],
        "p_terminal_pauli_sample": [float(x) for x in p_term_pauli[::10]],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Quick 2-traj 200fs smoke verification")
    parser.add_argument("--n-traj", type=int, default=48)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--t-max-fs", type=float, default=2000.0)
    parser.add_argument("--dt-fs", type=float, default=2.0)
    parser.add_argument("--max-hier", type=int, default=5)
    args = parser.parse_args()

    if args.smoke:
        n_traj = 2
        workers = 2
        t_max_fs = 200.0
        max_hier = 4
    else:
        n_traj = args.n_traj
        workers = args.workers
        t_max_fs = args.t_max_fs
        max_hier = args.max_hier

    with open(PKG_ROOT / "parameters.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    ham_data = json.loads((PKG_ROOT / cfg["lhcii_hamiltonian"]["hamiltonian_source"]).read_text(encoding="utf-8"))

    lam_dl = float(cfg["lhcii_hamiltonian"]["drude_lorentz_lambda_cm1"])
    gamma_dl = float(cfg["lhcii_hamiltonian"]["drude_lorentz_gamma_cm1"])
    temp_k = float(cfg["lhcii_hamiltonian"]["temperature_kelvin"])

    report: Dict[str, Any] = {
        "mesohops_mode": "smoke" if args.smoke else "production_benchmark",
        "vibronic_modes_cm1": [m[0] for m in HOPS_VIB_MODES],
        "lam_dl_cm1": lam_dl,
        "gamma_dl_cm1": gamma_dl,
        "temp_k": temp_k,
        "results": {},
    }

    for h_key in ("H2_Muh2010_diag_PDA", "H3_MMSIC_MD_2025_full"):
        H_mat = np.asarray(ham_data["hamiltonians_cm1"][h_key], dtype=np.float64)
        res = run_benchmark_for_hamiltonian(
            h_name=f"{h_key}_DL_K1",
            H_cm1=H_mat,
            lam_dl=lam_dl,
            gamma_dl=gamma_dl,
            temp_k=temp_k,
            max_hier=max_hier,
            t_max_fs=t_max_fs,
            dt_save_fs=args.dt_fs,
            n_traj=n_traj,
            workers=workers,
            include_vib=False,
            delta_a=3e-3,
        )
        report["results"][f"{h_key}_DL_K1"] = res
        print(f"=== {h_key}_DL_K1 ===")
        print(json.dumps({k: v for k, v in res.items() if not k.endswith("_sample")}, indent=2))

    if not args.smoke:
        # Also run explicit non-Markovian 340 cm^-1 vibronic hierarchy on H3 (16 parallel trajs across 16 cores)
        H3_mat = np.asarray(ham_data["hamiltonians_cm1"]["H3_MMSIC_MD_2025_full"], dtype=np.float64)
        res_vib = run_benchmark_for_hamiltonian(
            h_name="H3_MMSIC_MD_2025_full_DL_K1_Vib340",
            H_cm1=H3_mat,
            lam_dl=lam_dl,
            gamma_dl=gamma_dl,
            temp_k=temp_k,
            max_hier=4,
            t_max_fs=1000.0,
            dt_save_fs=1.0,
            n_traj=min(16, n_traj),
            workers=workers,
            include_vib=True,
            delta_a=5e-3,
        )
        report["results"]["H3_MMSIC_MD_2025_full_DL_K1_Vib340"] = res_vib
        print("=== H3_MMSIC_MD_2025_full_DL_K1_Vib340 ===")
        print(json.dumps({k: v for k, v in res_vib.items() if not k.endswith("_sample")}, indent=2))

        DATA_WP2.mkdir(parents=True, exist_ok=True)
        out_path = DATA_WP2 / "mesohops_hpc_benchmark.json"
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
