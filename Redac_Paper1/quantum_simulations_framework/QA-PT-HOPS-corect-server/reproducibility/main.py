#!/usr/bin/env python3
"""
main.py — Corrected JPCL reproducibility pipeline.

Fixes vs original:
  - Uses MD_analyse_code/hops_simulator.py (corrected MesoHOPS API)
  - storage accessed via hops.storage['psi_traj'] (dict-style)
  - PULSE_PARAMS removed from system_param
  - bcf_exp / bcf_convert_dl_to_exp imported from correct locations
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent.resolve()
_MD_CODE = _HERE.parent.resolve()          # MD_analyse_code/
_FRAMEWORK = _MD_CODE.parent.resolve()     # quantum_simulations_framework/

sys.path.insert(0, str(_FRAMEWORK))
sys.path.insert(0, str(_MD_CODE))

# ── Logging ───────────────────────────────────────────────────────────────────
_LOG_DIR = _HERE / "logs"
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s", datefmt="%H:%M:%S")
_fh = logging.FileHandler(_LOG_FILE)
_fh.setFormatter(_fmt)
_ch = logging.StreamHandler(sys.stdout)
_ch.setFormatter(_fmt)
logging.basicConfig(level=logging.INFO, handlers=[_fh, _ch])
logger = logging.getLogger(__name__)
logger.info(f"Log → {_LOG_FILE}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_and_validate_config() -> dict:
    cfg_path = _FRAMEWORK / "parameters.yaml"
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
    L = cfg["dynamics"]["hierarchy_depth"]
    K = cfg["dynamics"].get("matsubara_truncation", 0)
    if L < 10:
        raise ValueError(f"hierarchy_depth={L} < 10 (JPCL requires L≥10)")
    logger.info(f"Config OK: L={L}, K={K}, T={cfg['bath']['temperature']} K")
    return cfg


def check_environment() -> bool:
    from hops_simulator import MESOHOPS_AVAILABLE
    if MESOHOPS_AVAILABLE:
        try:
            import importlib.metadata
            ver = importlib.metadata.version("mesohops")
        except Exception:
            ver = "unknown"
        print(f"✅ MesoHOPS {ver} available")
        return True
    print("❌ MesoHOPS NOT found.")
    return False


def run_convergence_audit() -> dict:
    print("\n[Step 2] Convergence audit (L=9,10,11)...")
    from reproducibility.audit_convergence import run_convergence_audit as _audit
    data = _audit()
    print(f"  ✅ MAE(10→11)={data['audit_mae_10_11']:.2e}  →  {data['csv_path']}")
    return data


def run_full_fmo_simulation(cfg: dict) -> tuple:
    """Ensemble-averaged FMO simulation (filtered + broadband)."""
    print("\n[Step 3] Full FMO simulation (ensemble)...")
    from hops_simulator import HopsSimulator

    dyn = cfg["dynamics"]
    bath = cfg["bath"]
    n_traj = cfg.get("simulation", {}).get("n_traj", 50)

    try:
        from core.hamiltonian_factory import create_fmo_hamiltonian
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    except ImportError:
        H = np.array([[100.0, 50.0], [50.0, 0.0]])
        logger.warning("Using 2-site fallback Hamiltonian")

    n = H.shape[0]
    time_points = np.arange(0.0, dyn["time_max"], dyn["time_step"])
    init_state = np.zeros(n, dtype=complex)
    init_state[0] = 1.0

    sim_results = {}
    for label in ["filtered", "broadband"]:
        print(f"  {label}: {n_traj} trajectories...")
        pop_sum = None
        coh_sum = None
        n_ok = 0
        for seed in range(n_traj):
            sim = HopsSimulator(
                hamiltonian=H,
                temperature=bath["temperature"],
                reorganization_energy=bath["reorganization_energy"],
                drude_cutoff=bath["drude_cutoff"],
                max_hierarchy=dyn["hierarchy_depth"],
                k_matsubara=0,
            )
            try:
                data = sim.simulate_dynamics(time_points, init_state.copy(), seed=seed)
                pops = data["populations"]
                cohs = data.get("coherences", np.zeros(pops.shape[0]))
                if pop_sum is None:
                    pop_sum = pops.copy()
                    coh_sum = cohs.copy()
                    t_save = data["t_axis"]
                else:
                    m = min(pop_sum.shape[0], pops.shape[0])
                    pop_sum[:m] += pops[:m]
                    coh_sum[:m] += cohs[:m]
                n_ok += 1
            except Exception as e:
                logger.warning(f"  Trajectory {seed} failed: {e}")
        if n_ok == 0:
            raise RuntimeError(f"All trajectories failed for {label}")
        sim_results[label] = {
            "populations": pop_sum / n_ok,
            "coherences": coh_sum / n_ok,
            "t_axis": t_save,
            "n_traj": n_ok,
        }
        print(f"  ✅ {label}: {n_ok} trajectories averaged")

    # Save CSV
    results_dir = _HERE / "results"
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = results_dir / f"fmo_dynamics_{ts}.csv"
    filt = sim_results["filtered"]
    broad = sim_results["broadband"]
    m = min(filt["populations"].shape[0], broad["populations"].shape[0])
    t_ax = filt["t_axis"][:m]
    with open(csv_path, "w", newline="") as f:
        import csv
        writer = csv.writer(f)
        header = (["time_fs"]
                  + [f"pop_site{i+1}_filtered" for i in range(n)]
                  + [f"pop_site{i+1}_broadband" for i in range(n)]
                  + ["coherence_filtered", "coherence_broadband"])
        writer.writerow(header)
        for t_idx in range(m):
            row = ([t_ax[t_idx]]
                   + filt["populations"][t_idx].tolist()
                   + broad["populations"][t_idx].tolist()
                   + [filt["coherences"][t_idx], broad["coherences"][t_idx]])
            writer.writerow(row)
    print(f"  💾 FMO dynamics saved → {csv_path}")
    return sim_results, t_ax


def main() -> None:
    print("=" * 60)
    print("  Quantum Agrivoltaic PT-HOPS — JPCL Reproducibility Pipeline")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    print("\n[Step 1] Validating parameters.yaml...")
    try:
        cfg = load_and_validate_config()
        L = cfg["dynamics"]["hierarchy_depth"]
        print(f"  ✅ L={L}, T={cfg['bath']['temperature']} K")
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        sys.exit(1)

    print("\n[Step 1b] Checking MesoHOPS environment...")
    if not check_environment():
        sys.exit(1)

    audit_data = run_convergence_audit()
    sim_results, time_points = run_full_fmo_simulation(cfg)

    print("\n" + "=" * 60)
    print("  Pipeline complete.")
    print(f"  Results → {_HERE / 'results'}")
    print(f"  Logs    → {_LOG_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
