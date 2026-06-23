"""
Quantum Agrivoltaics Paper 2: Global Simulation Orchestrator.

Integrates FMO 8-site dynamics, NPoM dressing, Floquet Stark detuning,
microclimate FAO-56 Penman-Monteith water usage, and LCA (Net Ecological Benefit / Amortization).
"""

import os
import subprocess
import uuid
from datetime import datetime, timezone

import h5py
import numpy as np

from .config_loader import load_config

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from .constants import (
    BASELINE_TRANSMISSION,
    FLOQUET_EVAL_TIME_PS,
    MAX_TRAPPING_YIELD,
    MM_TO_LITER_PER_M2,
    N_DIM_DRESSED,
    PLASMON_INDEX,
    TRAPPING_SITES,
    WIND_SPEED_GREENHOUSE_FACTOR,
)
from .lca.database import AmortizationAnalysis
from .lca.neb import NetEcologicalBenefit
from .lca.plot_utils import Paper2FigureGenerator
from .logging_config import get_logger
from .microclimate.fao56 import GreenhouseEvapotranspiration
from .quantum_interface.diagnostics import NpomCoupling, SersDiagnostics
from .quantum_interface.hamiltonian import FmoHamiltonian
from .quantum_interface.pulse import FloquetStarkSwitch
from .quantum_interface.solver import MesoHopsSolver, QuantumStabilityAudit

logger = get_logger("orchestrator")


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
    logger.info("Run ID: %s | %s | Git: %s", run_id, timestamp, git_hash)

    config_path = os.path.join(_SCRIPT_DIR, "parameters.yaml")
    config = load_config(config_path)
    logger.info(
        "[1] Parameters loaded — Temperature: %s K, Solar flux: %s W/m2",
        config.simulation.temperature_k,
        solar_flux,
    )

    fmo_builder = FmoHamiltonian(config)
    H_fmo = fmo_builder.get_hamiltonian()

    floquet_switch = FloquetStarkSwitch(config)
    shift_matrix = floquet_switch.get_stark_detuning(solar_flux, time_ps=FLOQUET_EVAL_TIME_PS)
    H_fmo_active = H_fmo + shift_matrix

    npom = NpomCoupling(config)
    H_dressed = npom.dress_hamiltonian(H_fmo_active)
    logger.info("Dressed Hamiltonian built with size: %s", H_dressed.shape)

    t_max_fs = config.quantum.solver.simulation_duration_fs
    dt_fs = config.quantum.solver.time_step_fs
    time_points = np.arange(0.0, t_max_fs, dt_fs)
    n_steps = len(time_points)

    psi0 = np.zeros(N_DIM_DRESSED, dtype=complex)
    psi0[PLASMON_INDEX] = 1.0

    logger.info(
        "Propagating MesoHOPS trajectory for %d steps (dt=%.1f fs, t_max=%.0f fs)...",
        n_steps,
        dt_fs,
        t_max_fs,
    )
    solver = MesoHopsSolver(config)
    density_matrices = solver.propagate_dynamics(
        H_dressed,
        psi0,
        time_points,
        hierarchy_depth=config.quantum.solver.hierarchy_depth,
        n_traj=config.quantum.solver.n_traj,
    )

    dm_array = np.array(density_matrices)  # shape (n_steps, n_sites, n_sites)
    audit = QuantumStabilityAudit()
    audit_result = audit.audit(density_matrices)
    is_valid = audit_result.get("trace_ok", False) and audit_result.get("positivity_ok", False)
    logger.info(
        "Stability audit: %s", "SUCCESS" if is_valid else "FAILED — see logs/solver_errors.log"
    )

    gamma_rc = config.quantum.fmo.coupling_reaction_center
    trapped_pop = np.zeros(n_steps)
    for t in range(n_steps):
        trapped_pop[t] = sum(dm_array[t, s, s].real for s in TRAPPING_SITES)
    trap_yield = gamma_rc * np.sum(trapped_pop) * dt_fs
    trap_yield = min(max(trap_yield, 0.0), MAX_TRAPPING_YIELD)
    logger.info("Reaction center trapping yield (Phi_FT): %.4f", trap_yield)

    sers = SersDiagnostics(config)
    final_pop = np.diagonal(density_matrices[-1]).real
    sers_readout = sers.calculate_raman_spectrum(final_pop)
    logger.info("SERS Raman readout: %s", sers_readout)

    climate = GreenhouseEvapotranspiration(config)
    effective_transmission = floquet_switch.apply_omit_attenuation(
        solar_flux, baseline_transmission=BASELINE_TRANSMISSION
    )
    solar_flux_greenhouse = solar_flux * effective_transmission

    mc = config.microclimate
    wind_greenhouse = mc.default_wind_speed_m_s * WIND_SPEED_GREENHOUSE_FACTOR
    et_rate = climate.calculate_evapotranspiration(
        solar_flux_w_m2=solar_flux_greenhouse,
        temp_c=mc.default_temp_c,
        relative_humidity_pct=mc.default_rh_pct,
        wind_speed_m_s=wind_greenhouse,
    )
    logger.info("FAO-56 crop evapotranspiration (ET_c): %.4f mm/day", et_rate)

    lca_calc = NetEcologicalBenefit(config)
    lca_params = config.lca
    power_kwh = solar_flux * lca_params.pv_efficiency * lca_params.pv_fill_factor
    baseline_water_mm = mc.baseline_water_mm
    water_saved_l = max(0.0, baseline_water_mm - et_rate) * MM_TO_LITER_PER_M2

    neb_results = lca_calc.calculate_scenario_neb(
        scenario="A",
        excitonic_yield=trap_yield,
        water_saved_liters=water_saved_l,
        power_generated_kwh=power_kwh,
        crop_biomass_kg=lca_params.reference_biomass_kg,
    )
    logger.info(
        "LCA NEB assessment — Effective biomass: %.2f kg, Net carbon avoided: %.2f kg CO2e, FU: %.2f",
        neb_results["effective_biomass_kg"],
        neb_results["net_benefit_co2_kg"],
        neb_results["functional_unit"],
    )

    amortization = AmortizationAnalysis(config)
    capex = lca_params.default_capex
    revenue = lca_params.default_annual_revenue
    payback = amortization.calculate_payback_years(initial_capex=capex, annual_revenue=revenue)
    logger.info("CAPEX cooperative payback period: %.2f years", payback)

    h5_file = os.path.join(_SCRIPT_DIR, config.output.dynamics_h5)
    os.makedirs(os.path.dirname(h5_file), exist_ok=True)
    populations = dm_array.diagonal(axis1=1, axis2=2).real
    cumulative_yield = gamma_rc * np.cumsum(trapped_pop) * dt_fs
    with h5py.File(h5_file, "w") as f:
        dyn = f.create_group("dynamics")
        dyn.create_dataset("populations", data=populations)
        dyn.create_dataset("trapped_pop", data=trapped_pop)
        dyn.create_dataset("rc_yield", data=cumulative_yield)
        dyn.attrs["run_id"] = run_id
        dyn.attrs["git_hash"] = git_hash
        dyn.attrs["timestamp"] = timestamp
        dyn.attrs["time_step_fs"] = dt_fs
    logger.info("Dynamics serialized to HDF5: %s", h5_file)

    logger.info("[10] Generating publication figures...")
    fig_gen = Paper2FigureGenerator(
        output_dir=os.path.join(_SCRIPT_DIR, config.output.graphics_dir)
    )

    fig1_path = fig_gen.plot_figure_1_quantum_dynamics(h5_file)
    logger.info("Figure 1 saved to: %s", fig1_path)

    fig2_path = fig_gen.plot_figure_2_sers_readout(sers_readout)
    logger.info("Figure 2 saved to: %s", fig2_path)

    neb_scenario_b = lca_calc.calculate_scenario_neb(
        scenario="B",
        excitonic_yield=trap_yield * lca_params.scenario_b_yield_factor,
        water_saved_liters=water_saved_l * lca_params.scenario_b_water_factor,
        power_generated_kwh=power_kwh * lca_params.scenario_b_power_factor,
        crop_biomass_kg=lca_params.scenario_b_biomass_kg,
    )
    neb_scenario_c = lca_calc.calculate_scenario_neb(
        scenario="C",
        excitonic_yield=trap_yield * lca_params.scenario_c_yield_factor,
        water_saved_liters=lca_params.scenario_c_water_liters,
        power_generated_kwh=lca_params.scenario_c_power_kwh,
        crop_biomass_kg=lca_params.scenario_c_biomass_kg,
    )
    fig3_path = fig_gen.plot_figure_3_lca_neb(neb_results, neb_scenario_b, neb_scenario_c)
    logger.info("Figure 3 saved to: %s", fig3_path)
