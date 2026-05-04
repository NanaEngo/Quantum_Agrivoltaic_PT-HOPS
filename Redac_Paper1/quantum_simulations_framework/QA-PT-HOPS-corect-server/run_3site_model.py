#!/usr/bin/env python3
"""
run_3site_model.py — Corrected 3-site donor-bridge-acceptor PT-HOPS demo.

Fixes vs original:
  - Uses MD_analyse_code/hops_simulator.py (corrected MesoHOPS API)
  - Reads parameters from parameters.yaml (no hardcoded values)
  - Saves results to simulation_data/3site_dynamics_results.csv
"""

import sys
import csv
from pathlib import Path

import numpy as np
import yaml

# Add framework and MD_analyse_code to path
_HERE = Path(__file__).parent.resolve()
_FRAMEWORK = _HERE.parent.resolve()
sys.path.insert(0, str(_FRAMEWORK))
sys.path.insert(0, str(_HERE))

from hops_simulator import HopsSimulator, MESOHOPS_AVAILABLE


def load_config() -> dict:
    config_path = _FRAMEWORK / "parameters.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def run_3site_simulation() -> None:
    print("=" * 56)
    print(" PT-HOPS 3-Site Model — MesoHOPS corrected API ")
    print("=" * 56)

    if not MESOHOPS_AVAILABLE:
        print("❌ MesoHOPS not found. Install it first.")
        sys.exit(1)

    cfg = load_config()
    dyn = cfg["dynamics"]
    bath = cfg["bath"]

    # 3-site donor-bridge-acceptor Hamiltonian (cm^-1)
    H = np.array([
        [0.0,   -80.0,   5.0],
        [-80.0,  150.0, -50.0],
        [5.0,   -50.0,  -50.0],
    ])
    print(f"Hamiltonian (3 sites):\n{H}\n")

    sim = HopsSimulator(
        hamiltonian=H,
        temperature=bath["temperature"],
        reorganization_energy=bath["reorganization_energy"],
        drude_cutoff=bath["drude_cutoff"],
        max_hierarchy=dyn["hierarchy_depth"],
        k_matsubara=dyn.get("matsubara_truncation", 0),
    )
    print(f"Simulator type : {sim.simulator_type}")
    print(f"Using MesoHOPS : {sim.is_using_mesohops}\n")

    time_points = np.arange(0.0, dyn["time_max"], dyn["time_step"])
    initial_state = np.array([1.0, 0.0, 0.0], dtype=complex)

    print(f"Running simulation (L={dyn['hierarchy_depth']}, "
          f"dt={dyn['time_step']} fs, T={bath['temperature']} K)...")
    results = sim.simulate_dynamics(time_points, initial_state)

    pops = results["populations"]
    t_ax = results["t_axis"]
    print(f"\n✓ Done — {len(t_ax)} time points")
    print(f"  Final populations: "
          f"site1={pops[-1, 0]:.3f}, site2={pops[-1, 1]:.3f}, site3={pops[-1, 2]:.3f}")

    # Save results
    out_dir = _FRAMEWORK.parent / "simulation_data"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "3site_dynamics_results.csv"

    cohs = results.get("coherences", np.zeros(len(t_ax)))
    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time_fs", "pop_1", "pop_2", "pop_3", "coherence"])
        for i, t in enumerate(t_ax):
            writer.writerow([t, pops[i, 0], pops[i, 1], pops[i, 2], cohs[i]])
    print(f"  Saved → {out_file}")


if __name__ == "__main__":
    run_3site_simulation()
