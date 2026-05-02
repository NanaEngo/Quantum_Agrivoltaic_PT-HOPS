#!/usr/bin/env python
# coding: utf-8
"""
Run the 3-site model to demonstrate generalizability of spectral bath engineering.
All physics parameters read from parameters.yaml — no hardcoded values.
"""

import sys
import yaml
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.absolute()))

from utils.logging_config import setup_logging, get_logger
setup_logging(level=20)
logger = get_logger("run_3site_model")

from core import HopsSimulator


def load_config():
    config_path = Path(__file__).parent / "parameters.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_3site_simulation():
    print("=" * 56)
    print(" PT-HOPS 3-Site Model Generalizability Demonstration ")
    print("=" * 56)

    cfg = load_config()
    dyn = cfg['dynamics']
    bath = cfg['bath']

    # 3-site donor-bridge-acceptor Hamiltonian (cm^-1)
    H_3site = np.array([
        [0.0,   -80.0,  5.0],
        [-80.0,  150.0, -50.0],
        [5.0,   -50.0, -50.0]
    ])
    print(f"Hamiltonian (3 sites):\n{H_3site}")

    simulator = HopsSimulator(
        hamiltonian=H_3site,
        temperature=bath['temperature'],
        reorganization_energy=bath['reorganization_energy'],
        drude_cutoff=bath['drude_cutoff'],
        max_hierarchy=dyn['hierarchy_depth'],
        k_matsubara=dyn['matsubara_truncation'],
        use_mesohops=True,
        use_sbd=True,
        use_pt_hops=True,
    )

    time_points = np.arange(0, dyn['time_max'], dyn['time_step'])
    initial_state = np.array([1.0, 0.0, 0.0], dtype=complex)

    print(f"\nRunning PT-HOPS (L={dyn['hierarchy_depth']}, K={dyn['matsubara_truncation']}, "
          f"dt={dyn['time_step']} fs, T={bath['temperature']} K)...")
    results = simulator.simulate_dynamics(time_points, initial_state)

    pops = results['populations']
    print(f"\n✓ Done — final populations: "
          f"site1={pops[-1,0]:.3f}, site2={pops[-1,1]:.3f}, site3={pops[-1,2]:.3f}")

    output_dir = Path(__file__).parent.parent / "simulation_data"
    output_dir.mkdir(exist_ok=True)
    out_file = output_dir / "3site_dynamics_results.csv"
    data = np.column_stack((
        results['t_axis'], pops,
        results.get('coherences', np.zeros_like(results['t_axis']))
    ))
    np.savetxt(out_file, data, delimiter=",",
               header="time_fs,pop_1,pop_2,pop_3,coherence", comments="")
    print(f"  Saved to: {out_file}")


if __name__ == "__main__":
    run_3site_simulation()
