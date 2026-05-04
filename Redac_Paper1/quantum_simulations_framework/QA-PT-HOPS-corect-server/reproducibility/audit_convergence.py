#!/usr/bin/env python3
"""
audit_convergence.py — L=9,10,11 hierarchy convergence audit.

Fixes vs original:
  - Uses MD_analyse_code/hops_simulator.py (corrected MesoHOPS API)
  - Removed bcf_convert_dl_to_exp / bcf_exp import errors
  - storage accessed via hops.storage['psi_traj'] (dict-style)
  - PULSE_PARAMS removed from system_param
"""

import os
import sys
import csv
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml

_HERE = Path(__file__).parent.resolve()
_FRAMEWORK = _HERE.parent.parent.resolve()
sys.path.insert(0, str(_FRAMEWORK))
sys.path.insert(0, str(_HERE.parent))   # MD_analyse_code

from hops_simulator import HopsSimulator, MESOHOPS_AVAILABLE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_config() -> dict:
    config_path = _FRAMEWORK / "parameters.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def run_convergence_audit() -> dict:
    """Run L=9,10,11 convergence audit. Returns audit metrics dict."""
    print("🧪 Starting L=9,10,11 Convergence Audit...")

    if not MESOHOPS_AVAILABLE:
        print("❌ MesoHOPS not found. Cannot run convergence audit.")
        sys.exit(1)

    cfg = load_config()
    dyn = cfg["dynamics"]
    bath = cfg["bath"]

    # Use shorter time window for audit (tests hierarchy depth, not full dynamics)
    t_audit = min(200.0, dyn["time_max"])
    dt = dyn["time_step"]
    time_points = np.arange(0.0, t_audit, dt)

    # FMO Hamiltonian (7-site, cm^-1) — standard literature values
    try:
        from core.hamiltonian_factory import create_fmo_hamiltonian
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    except ImportError:
        # Minimal 2-site fallback for testing
        H = np.array([[100.0, 50.0], [50.0, 0.0]])
        logger.warning("hamiltonian_factory not found, using 2-site test Hamiltonian")

    n = H.shape[0]
    init_state = np.zeros(n, dtype=complex)
    init_state[0] = 1.0

    depths = [9, 10, 11]
    results = {}

    for L in depths:
        logger.info(f"Running L={L}...")
        sim = HopsSimulator(
            hamiltonian=H,
            temperature=bath["temperature"],
            reorganization_energy=bath["reorganization_energy"],
            drude_cutoff=bath["drude_cutoff"],
            max_hierarchy=L,
            k_matsubara=0,   # DL-only bath for audit
        )
        data = sim.simulate_dynamics(time_points, initial_state=init_state.copy(), seed=0)
        results[L] = data["populations"]
        logger.info(f"  L={L}: done, shape={results[L].shape}")

    # Sanity: L=9 and L=10 must differ (otherwise hierarchy is not active)
    if np.allclose(results[9], results[10], atol=1e-12):
        print("❌ FATAL: L=9 and L=10 are identical — hierarchy not active.")
        sys.exit(1)

    # Positivity check
    for L in depths:
        min_pop = np.min(results[L])
        if min_pop < -1e-3:
            print(f"❌ FATAL: Positivity violated at L={L} (min={min_pop:.2e})")
            sys.exit(1)
    print("✅ Positivity checks passed.")

    # Convergence metrics
    n_min = min(r.shape[0] for r in results.values())
    mae_9_10 = float(np.mean(np.abs(results[10][:n_min] - results[9][:n_min])))
    mae_10_11 = float(np.mean(np.abs(results[11][:n_min] - results[10][:n_min])))

    threshold = cfg["dynamics"].get("convergence_threshold", 1e-3)
    print(f"\n📊 Convergence Audit Results:")
    print(f"   MAE (L=9 → L=10)  : {mae_9_10:.2e}")
    print(f"   MAE (L=10 → L=11) : {mae_10_11:.2e}")
    if mae_10_11 < threshold:
        print(f"✅ L=10 is converged (residual < {threshold:.1e})")
    else:
        print(f"⚠️  Residual {mae_10_11:.2e} exceeds threshold {threshold:.1e}")

    # Save CSV
    results_dir = _HERE / "results"
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = results_dir / f"convergence_audit_{ts}.csv"

    t_ax = time_points[:n_min]
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["time_fs"] + [f"pop_site{i+1}_L{L}" for L in depths for i in range(n)]
        writer.writerow(header)
        for t_idx in range(n_min):
            row = [t_ax[t_idx]]
            for L in depths:
                row.extend(results[L][t_idx].tolist())
            writer.writerow(row)
    print(f"💾 Audit data saved → {csv_path}")

    return {
        "time_points": t_ax,
        "populations": results[10][:n_min],
        "audit_mae_9_10": mae_9_10,
        "audit_mae_10_11": mae_10_11,
        "csv_path": str(csv_path),
    }


if __name__ == "__main__":
    run_convergence_audit()
