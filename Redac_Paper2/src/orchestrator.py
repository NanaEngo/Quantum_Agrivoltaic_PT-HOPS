"""
Quantum Agrivoltaics Paper 2: Global Simulation Orchestrator.

Integrates FMO 8-site dynamics, NPoM dressing, Floquet Stark detuning,
microclimate FAO-56 Penman-Monteith water usage, and LCA (Net Ecological Benefit / Amortization).
"""

import os
import sys
import uuid
import subprocess
import numpy as np
from datetime import datetime, timezone

# Ensure project root is on the path for relative sibling imports
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from src.config_loader import load_config
from src.quantum_interface.hamiltonian import FmoHamiltonian
from src.quantum_interface.diagnostics import NpomCoupling, SersDiagnostics
from src.quantum_interface.pulse import FloquetStarkSwitch
from src.quantum_interface.solver import QuantumStabilityAudit, MesoHopsSolver
from src.microclimate.fao56 import GreenhouseEvapotranspiration
from src.lca.neb import NetEcologicalBenefit
from src.lca.database import AmortizationAnalysis
from src.lca.plot_utils import Paper2FigureGenerator


def _get_git_hash() -> str:
    """Return the short Git commit hash of the current HEAD, or 'unknown'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=_SCRIPT_DIR,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return "unknown"


def _generate_run_id() -> str:
    """Generate a unique run identifier (UUID4 truncated to 8 chars)."""
    return uuid.uuid4().hex[:8]


def run_global_simulation(solar_flux: float) -> None:
    """Run the complete Paper 2 simulation pipeline from configuration to figures."""

    run_id = _generate_run_id()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    git_hash = _get_git_hash()
    print(f"--- Run ID: {run_id} | {timestamp} | Git: {git_hash} ---")

    # 1. Load Configuration
    config_path = os.path.join(_SCRIPT_DIR, "parameters.yaml")
    config = load_config(config_path)
    print("--- [1] Parameters Loaded ---")
    print(f"Temperature: {config.simulation.temperature_k} K")
    print(
        f"Solar flux: {solar_flux} W/m2 (Threshold: {config.simulation.solar_flux_threshold} W/m2)"
    )

    # 2. Build Hamiltonian & Trapping Sink
    fmo_builder = FmoHamiltonian(config)
    H_fmo = fmo_builder.get_hamiltonian()

    # 3. Apply Floquet Stark Detuning Switch
    floquet_switch = FloquetStarkSwitch(config)
    shift_matrix = floquet_switch.get_stark_detuning(solar_flux, time_ps=1.0)
    H_fmo_active = H_fmo + shift_matrix

    # 4. Dress Hamiltonian via NPoM Coupling
    npom = NpomCoupling(config)
    H_dressed = npom.dress_hamiltonian(H_fmo_active)
    print(f"Dressed Hamiltonian built with size: {H_dressed.shape}")

    # 5. Simulate Dynamics using MesoHOPS Solver
    time_points = np.arange(0.0, 100.0, 5.0)
    n_steps = len(time_points)

    # Initial state: localized excitation on the plasmon mode (index 8)
    psi0 = np.zeros(9, dtype=complex)
    psi0[8] = 1.0

    print(f"Running MesoHOPS trajectory propagation for {n_steps} steps...")
    solver = MesoHopsSolver(config)
    density_matrices = solver.propagate_dynamics(H_dressed, psi0, time_points, n_traj=2)

    # Audit trajectory stability
    audit = QuantumStabilityAudit(config)
    is_valid = audit.audit_trajectory(density_matrices)
    print(
        f"Stability Audit Result: {'SUCCESS' if is_valid else 'FAILED (See logs/solver_errors.log)'}"
    )

    # Calculate forward transfer yield (time integrated trapping population)
    gamma_rc = config.quantum.fmo.coupling_reaction_center
    trapped_pop = np.zeros(n_steps)
    for t in range(n_steps):
        trapped_pop[t] = density_matrices[t, 2, 2].real + density_matrices[t, 3, 3].real
    trap_yield = 2.0 * gamma_rc * np.sum(trapped_pop) * 5.0
    trap_yield = min(max(trap_yield, 0.0), 0.98)
    print(f"Reaction Center Trapping Yield (Phi_FT): {trap_yield:.4f}")

    # 6. SERS Optomechanical Diagnostics Readout
    sers = SersDiagnostics(config)
    final_pop = np.diagonal(density_matrices[-1]).real
    sers_readout = sers.calculate_raman_spectrum(final_pop)
    print("SERS Raman Readout peak intensities:")
    for mode, val in sers_readout.items():
        print(f"  Mode {mode}: {val:.4f}")

    # 7. Evapotranspiration Crop water usage (FAO-56 Penman-Monteith)
    climate = GreenhouseEvapotranspiration(config)
    effective_transmission = floquet_switch.apply_omit_attenuation(
        solar_flux, baseline_transmission=0.8
    )
    solar_flux_greenhouse = solar_flux * effective_transmission

    et_rate = climate.calculate_evapotranspiration(
        solar_flux_w_m2=solar_flux_greenhouse,
        temp_c=25.0,
        relative_humidity_pct=60.0,
        wind_speed_m_s=1.5,
    )
    print(f"FAO-56 Crop Evapotranspiration (ET_c): {et_rate:.4f} mm/day")

    # 8. LCA Net Ecological Benefit (NEB) calculation
    lca_calc = NetEcologicalBenefit(config)
    power_kwh = solar_flux * 0.15 * 0.8
    water_saved_l = max(0.0, 5.0 - et_rate) * 1000.0

    neb_results = lca_calc.calculate_scenario_neb(
        scenario="A",
        excitonic_yield=trap_yield,
        water_saved_liters=water_saved_l,
        power_generated_kwh=power_kwh,
        crop_biomass_kg=12.0,
    )
    print("LCA NEB Assessment:")
    print(f"  Effective Biomass: {neb_results['effective_biomass_kg']:.2f} kg")
    print(f"  Net Carbon Avoided: {neb_results['net_benefit_co2_kg']:.2f} kg CO2e")
    print(f"  Functional Unit Value: {neb_results['functional_unit']:.2f}")

    # 9. Socioeconomic Amortization
    amortization = AmortizationAnalysis(config)
    payback = amortization.calculate_payback_years(
        initial_capex=25000.0, annual_revenue=6000.0
    )
    print(f"CAPEX Cooperative Payback Period: {payback:.2f} years")

    # Save finalized dynamics HDF5 file with enriched metadata
    h5_file = os.path.join(_SCRIPT_DIR, "data/converged/production_dynamics.h5")
    populations = density_matrices.diagonal(axis1=1, axis2=2).real
    audit.serialize_to_hdf5(
        h5_file,
        populations,
        trapped_pop,
        run_id=run_id,
        git_hash=git_hash,
        timestamp=timestamp,
    )
    print(f"Dynamics serialized to HDF5: {h5_file}")

    # 10. Publication Figure Generation
    print("--- [10] Generating Q1 Publication Figures ---")
    fig_gen = Paper2FigureGenerator(output_dir=os.path.join(_SCRIPT_DIR, "Graphics"))

    fig1_path = fig_gen.plot_figure_1_quantum_dynamics(h5_file)
    print(f"  Figure 1 saved to: {fig1_path}")

    fig2_path = fig_gen.plot_figure_2_sers_readout(sers_readout)
    print(f"  Figure 2 saved to: {fig2_path}")

    # Scenario B & C for comparison
    neb_scenario_b = lca_calc.calculate_scenario_neb(
        scenario="B",
        excitonic_yield=trap_yield * 0.8,
        water_saved_liters=water_saved_l * 0.9,
        power_generated_kwh=power_kwh * 1.1,
        crop_biomass_kg=10.0,
    )
    neb_scenario_c = lca_calc.calculate_scenario_neb(
        scenario="C",
        excitonic_yield=trap_yield * 0.7,
        water_saved_liters=0.0,
        power_generated_kwh=0.0,
        crop_biomass_kg=12.0,
    )
    fig3_path = fig_gen.plot_figure_3_lca_neb(neb_results, neb_scenario_b, neb_scenario_c)
    print(f"  Figure 3 saved to: {fig3_path}")
