#!/usr/bin/env python3
"""
quantum_coherence_agrivoltaics_mesohops_complete.py
Corrected main simulation script for Quantum Agrivoltaics with MesoHOPS.

Key fixes vs original:
  1. bcf_exp imported from mesohops.trajectory.exp_noise (correct location)
  2. bcf_convert_dl_to_exp from mesohops.util.bath_corr_functions (correct name,
     was wrongly called bcf_convert_sdl_to_exp in some versions)
  3. PULSE_PARAMS removed from system_param (not a valid MesoHOPS key)
  4. storage accessed via hops.storage['psi_traj'] dict-style
  5. storage_param={'psi_traj': True, 't_axis': True} passed to HopsTrajectory
  6. Uses MD_analyse_code/hops_simulator.py as the simulation backend
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path

import numpy as np

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent.resolve()          # MD_analyse_code/
_FRAMEWORK = _HERE.parent.resolve()              # quantum_simulations_framework/
sys.path.insert(0, str(_FRAMEWORK))
sys.path.insert(0, str(_HERE))

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── MesoHOPS availability check ───────────────────────────────────────────────
try:
    from mesohops.trajectory.hops_trajectory import HopsTrajectory
    from mesohops.trajectory.exp_noise import bcf_exp                        # ✓ correct
    from mesohops.util.bath_corr_functions import bcf_convert_dl_to_exp      # ✓ correct name
    MESOHOPS_AVAILABLE = True
    logger.info("MesoHOPS imported successfully")
except ImportError as e:
    logger.warning(f"MesoHOPS not available: {e}")
    MESOHOPS_AVAILABLE = False

print("Quantum Agrivoltaics Framework — MesoHOPS (corrected)")
print("=" * 55)
print(f"Date          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"MesoHOPS      : {MESOHOPS_AVAILABLE}")
print()

# ── Configuration ─────────────────────────────────────────────────────────────
config_path = _FRAMEWORK / "data_input" / "quantum_agrivoltaics_params.json"
if config_path.exists():
    with open(config_path) as f:
        config = json.load(f)
    print(f"✓ Config loaded: T={config['simulation_params']['temperature']} K")
else:
    config = None
    print("⚠ Config not found, using defaults")

# ── Output directories ────────────────────────────────────────────────────────
sim_data_dir = _FRAMEWORK.parent / "simulation_data"
graphics_dir = _FRAMEWORK.parent / "Graphics"
sim_data_dir.mkdir(exist_ok=True)
graphics_dir.mkdir(exist_ok=True)

# ── Framework imports ─────────────────────────────────────────────────────────
from core.constants import (
    DEFAULT_MAX_HIERARCHY,
    DEFAULT_MAX_TIME,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIME_POINTS,
    FMO_SITE_ENERGIES_7,
    FMO_COUPLINGS,
)
from core.hamiltonian_factory import create_fmo_hamiltonian
from hops_simulator import HopsSimulator   # corrected simulator

print(f"✓ Framework modules imported")
print(f"  FMO site energies : {FMO_SITE_ENERGIES_7}")
print(f"  Default T         : {DEFAULT_TEMPERATURE} K")
print()

# ── FMO Hamiltonian ───────────────────────────────────────────────────────────
H_fmo, fmo_energies = create_fmo_hamiltonian()
print(f"✓ FMO Hamiltonian: shape={H_fmo.shape}")
print()

# ── Simulator initialisation ──────────────────────────────────────────────────
print("Initialising HopsSimulator (corrected MesoHOPS API)...")
simulator = HopsSimulator(
    H_fmo,
    temperature=DEFAULT_TEMPERATURE,
    use_mesohops=True,
    max_hierarchy=DEFAULT_MAX_HIERARCHY,
)
print(f"✓ Simulator type   : {simulator.simulator_type}")
print(f"  Using MesoHOPS   : {simulator.is_using_mesohops}")
print()

# ── Quantum dynamics simulation ───────────────────────────────────────────────
print("Running quantum dynamics simulation...")
time_points = np.linspace(0, DEFAULT_MAX_TIME, DEFAULT_TIME_POINTS)
initial_state = np.zeros(H_fmo.shape[0], dtype=complex)
initial_state[0] = 1.0   # Excite site 1

results = simulator.simulate_dynamics(time_points=time_points, initial_state=initial_state)

pops = results["populations"]
t_ax = results["t_axis"]
print(f"✓ Simulation complete")
print(f"  Time points      : {len(t_ax)}")
print(f"  Population shape : {pops.shape}")
print(f"  Initial pop(1)   : {pops[0, 0]:.4f}")
print(f"  Final pop(1)     : {pops[-1, 0]:.4f}")
transfer_eff = 1.0 - pops[-1, 0]
print(f"  Transfer eff.    : {transfer_eff * 100:.2f}%")
print()

# ── Save results ──────────────────────────────────────────────────────────────
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_csv = sim_data_dir / f"quantum_dynamics_{ts}.csv"

import csv
cohs = results.get("coherences", np.zeros(len(t_ax)))
with open(out_csv, "w", newline="") as f:
    writer = csv.writer(f)
    header = ["time_fs"] + [f"pop_site{i+1}" for i in range(pops.shape[1])] + ["coherence"]
    writer.writerow(header)
    for i, t in enumerate(t_ax):
        writer.writerow([t] + pops[i].tolist() + [cohs[i]])
print(f"✓ Results saved → {out_csv}")
print()

# ── Summary ───────────────────────────────────────────────────────────────────
print("=" * 55)
print("SUMMARY")
print("=" * 55)
print(f"  Simulator        : {simulator.simulator_type}")
print(f"  FMO sites        : {H_fmo.shape[0]}")
print(f"  Time range       : 0 – {DEFAULT_MAX_TIME} fs ({len(t_ax)} pts)")
print(f"  Transfer eff.    : {transfer_eff * 100:.2f}%")
print(f"  Output CSV       : {out_csv}")
print("=" * 55)
