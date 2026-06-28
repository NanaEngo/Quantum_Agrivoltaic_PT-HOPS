"""
Quantum Agrivoltaics Paper 2: Global Simulation Orchestrator.

Integrates FMO 8-site dynamics, NPoM dressing, Floquet Stark detuning,
microclimate FAO-56 Penman-Monteith water usage, and LCA (Net Ecological Benefit / Amortization).
"""

import os
import subprocess
import time as _time
import uuid
from datetime import datetime, timezone

import h5py
import numpy as np

from .algorithms.qaoa_optimizer import QAOAOptimizer
from .config_loader import load_config
from .digital_twin import DigitalTwin
from .geophysics.quantum_gravimetry import QuantumGravimeter
from .iot_security.data_sovereignty import DataSovereigntyProtocol
from .materials.zwitterionic_coating import ZwitterionicCoating

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from .constants import (
    BASELINE_TRANSMISSION,
    FLOQUET_EVAL_TIME_PS,
    FMO_NSITES,
    MAX_TRAPPING_YIELD,
    MM_TO_LITER_PER_M2,
    N_DIM_DRESSED,
    PLASMON_INDEX,
    TRAPPING_SITES,
    WIND_SPEED_GREENHOUSE_FACTOR,
)
from .lca.neb import NetEcologicalBenefit
from .lca.plot_utils import Paper2FigureGenerator
from .logging_config import get_logger
from .microclimate.fao56 import GreenhouseEvapotranspiration
from .quantum_interface.diagnostics import NpomCoupling, SersDiagnostics
from .quantum_interface.hamiltonian import FmoHamiltonian
from .quantum_interface.pulse import FloquetStarkSwitch
from .quantum_interface.signal_processing import detect_stress_anomaly
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
    _t0 = _time.time()
    _t_phase = _t0

    run_id = _generate_run_id()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    git_hash = _get_git_hash()
    logger.info("Run ID: %s | %s | Git: %s", run_id, timestamp, git_hash)

    config_path = os.path.join(_SCRIPT_DIR, "parameters.yaml")
    config = load_config(config_path)
    logger.info(
        "[1/10] Parameters loaded — Temperature: %s K, Solar flux: %s W/m2 (%s)",
        config.simulation.temperature_k,
        solar_flux,
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()

    fmo_builder = FmoHamiltonian(config)
    H_fmo = fmo_builder.get_hamiltonian()

    floquet_switch = FloquetStarkSwitch(config)
    shift_matrix = floquet_switch.get_stark_detuning(solar_flux, time_ps=FLOQUET_EVAL_TIME_PS)
    H_fmo_active = H_fmo + shift_matrix

    npom = NpomCoupling(config)
    if config.quantum.npom.enabled:
        H_dressed = npom.dress_hamiltonian(H_fmo_active)
        logger.info(
            "[2/10] Hamiltonian built (NPoM ON, size=%s) (%s)",
            H_dressed.shape,
            f"{_time.time() - _t_phase:.1f}s",
        )
    else:
        H_dressed = H_fmo_active
        logger.info(
            "[2/10] Hamiltonian built (NPoM OFF, size=%s) (%s)",
            H_dressed.shape,
            f"{_time.time() - _t_phase:.1f}s",
        )
    _t_phase = _time.time()

    t_max_fs = config.quantum.solver.simulation_duration_fs
    dt_fs = config.quantum.solver.time_step_fs
    time_points = np.arange(0.0, t_max_fs, dt_fs)
    n_steps = len(time_points)

    if config.quantum.npom.enabled:
        psi0 = np.zeros(N_DIM_DRESSED, dtype=complex)
        psi0[PLASMON_INDEX] = 1.0
    else:
        psi0 = np.zeros(FMO_NSITES, dtype=complex)
        psi0[0] = 1.0

    n_traj = config.quantum.solver.n_traj
    logger.info(
        "[3/10] Propagating %d trajectories × %d steps (dt=%.1f fs, t_max=%.0f fs) (%s)",
        n_traj,
        n_steps,
        dt_fs,
        t_max_fs,
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()
    solver = MesoHopsSolver(config)
    density_matrices = solver.propagate_dynamics(
        H_dressed,
        psi0,
        time_points,
        hierarchy_depth=config.quantum.solver.hierarchy_depth,
        n_traj=n_traj,
    )

    logger.info(
        "[4/10] Propagation complete — %d DM matrices (%s/%s)",
        len(density_matrices),
        f"{_time.time() - _t_phase:.1f}s" if density_matrices else "FAILED",
        f"{_time.time() - _t0:.1f}s total",
    )
    _t_phase = _time.time()

    if not density_matrices:
        logger.error(
            "[4/10] No density matrices returned — aborting downstream analysis.", exc_info=True
        )
        return

    dm_array = np.array(density_matrices)
    audit = QuantumStabilityAudit()
    audit_result = audit.audit(density_matrices)
    is_valid = audit_result.get("trace_ok", False) and audit_result.get("positivity_ok", False)
    logger.info(
        "[5/10] Stability audit: %s (%s)",
        "SUCCESS" if is_valid else "FAILED",
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()

    gamma_rc = config.quantum.fmo.coupling_reaction_center
    trapped_pop = np.sum(dm_array[:, TRAPPING_SITES, TRAPPING_SITES].real, axis=1)
    # Consistent with SI Eq. \ref{eq:SI_phi_ft}: \Phi_FT = 2 \Gamma_RC \int (P3+P4) dt
    trap_yield = 2.0 * gamma_rc * np.sum(trapped_pop) * dt_fs
    trap_yield = min(max(trap_yield, 0.0), MAX_TRAPPING_YIELD)
    logger.info(
        "[6/10] Reaction center trapping yield (Phi_FT): %.4f (%s)",
        trap_yield,
        f"{_time.time() - _t_phase:.1f}s",
    )

    # --- V5: Dynamic soiling attenuation & global canopy yield ---
    days_since_cleaning = getattr(config.microclimate.greenhouse, "days_since_cleaning", 30)
    daily_decay_rate = config.physics.soiling_decay_rate_per_day
    power_ideal_kwh = solar_flux * config.lca.pv_efficiency * config.lca.pv_fill_factor
    power_soiled_kwh = SersDiagnostics.calculate_opv_power_with_soiling(
        power_ideal=power_ideal_kwh,
        days_since_cleaning=days_since_cleaning,
        daily_decay_rate=daily_decay_rate,
    )
    soiling_factor_applied = power_soiled_kwh / max(power_ideal_kwh, 1e-9)
    logger.info(
        "[6b/10] OPV soiling — %.0f days since clean, factor=%.3f, P_soiled=%.3f kWh",
        days_since_cleaning,
        soiling_factor_applied,
        power_soiled_kwh,
    )
    # Φ_FT is the physical forward transfer yield = Γ_RC × ∫(P₃+P₄)dt (Eq. 2)
    # For the norm decay of the non-Hermitian Hamiltonian, the factor is 2Γ_RC,
    # but the manuscript defines Φ_FT without the factor of 2 for readability.
    physical_yield_npom = trap_yield  # already the physical yield
    phi_ft_passive = 0.98  # known baseline Φ_FT (NPoM OFF, N=1000 dedicated run)
    sers_obj = SersDiagnostics(config)
    phi_ft_global = sers_obj.calculate_global_canopy_yield(
        phi_ft_npom=physical_yield_npom,
        phi_ft_passive=phi_ft_passive,
        sentinel_ratio=config.physics.sensing_sentinel_ratio,
    )
    logger.info(
        "[6c/10] Global canopy yield — Phi_FT_NPoM(raw)=%.4f, "
        "Phi_FT_NPoM(physical)=%.4f, Phi_FT_passive=%.4f, "
        "Phi_FT_global=%.4f (sentinel_ratio=%.2f%%)",
        trap_yield,
        physical_yield_npom,
        phi_ft_passive,
        phi_ft_global,
        config.physics.sensing_sentinel_ratio * 100,
    )
    _t_phase = _time.time()

    # --- V6: Agrivoltaic Digital Twin fusion (Axe 1) ---
    dt = DigitalTwin(config)
    dt_state = dt.tick(
        solar_flux=solar_flux,
        dm_array=dm_array,
    )
    logger.info(
        "[6d/10] Digital Twin tick #%d — urgency=%s, phi_ft_global=%.4f, "
        "et_rate=%.4f mm/day, water_saved=%.1f L/m2, power_soiled=%.3f kWh, "
        "CO2_avoided=%.2f kg (%s)",
        dt_state["tick"],
        dt_state["urgency"],
        dt_state["phi_ft_global"],
        dt_state["et_rate_mm_day"],
        dt_state["water_saved_liters"],
        dt_state["power_soiled_kwh"],
        dt_state["neb_co2_kg"],
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()

    sers = SersDiagnostics(config)
    final_pop = np.diagonal(density_matrices[-1]).real
    sers_readout = sers.calculate_raman_spectrum(final_pop)
    logger.info(
        "[7/10] SERS Raman readout: %s (%s)", sers_readout, f"{_time.time() - _t_phase:.1f}s"
    )
    _t_phase = _time.time()

    # --- V6: QML signal processing on SERS readout (Axe 6) ---
    # Build a synthetic noisy spectrum from the SERS output + reference dictionary
    sers_sig = config.quantum_signal
    raman_vals = np.array(
        [
            sers_readout.get("180_cm", 0.0),
            sers_readout.get("740_cm", 0.0),
            sers_readout.get("1145_cm", 0.0),
        ]
    )
    # Inject realistic greenhouse noise (shot + thermal) — configurable fraction
    noise_fraction = sers_sig.noise_sigma_fraction
    noise_level = noise_fraction * np.maximum(raman_vals, 1.0)
    noisy_spectrum = raman_vals + np.random.normal(0.0, noise_level)
    noisy_spectrum = np.maximum(noisy_spectrum, 0.0)

    # Reference dictionary: 3 canonical stress states
    ref_dict = np.array(
        [
            [100.0, 50.0, 20.0],  # healthy baseline
            [60.0, 80.0, 120.0],  # moderate oxidative stress
            [20.0, 10.0, 200.0],  # severe stress / pesticide contamination
        ],
        dtype=np.float64,
    )
    ref_labels = np.array([0.0, 0.4, 0.9], dtype=np.float64)  # 0 = healthy, 1 = critical

    anomaly_result = detect_stress_anomaly(
        noisy_spectrum=noisy_spectrum,
        reference_dictionary=ref_dict,
        reference_labels=ref_labels,
        gamma=sers_sig.kernel_gamma,
        regularization=sers_sig.kernel_regularization,
        zscore_threshold=sers_sig.stress_anomaly_zscore,
        mps_chi=sers_sig.mps_chi,
    )
    logger.info(
        "[7b/10] QML signal processing — stress=%.3f, anomaly=%.3f, early_warning=%s (%s)",
        anomaly_result["predicted_stress"],
        anomaly_result["anomaly_score"],
        anomaly_result["early_warning"],
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()

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
    logger.info("[8/10] FAO-56 ET_c: %.4f mm/day (%s)", et_rate, f"{_time.time() - _t_phase:.1f}s")
    _t_phase = _time.time()

    lca_calc = NetEcologicalBenefit(config)
    lca_params = config.lca
    power_kwh = power_soiled_kwh  # V5: use soiling-adjusted power
    baseline_water_mm = mc.baseline_water_mm
    water_saved_l = max(0.0, baseline_water_mm - et_rate) * MM_TO_LITER_PER_M2

    neb_results = lca_calc.calculate_scenario_neb(
        scenario="A",
        excitonic_yield=phi_ft_global,  # V5: use area-weighted global yield
        water_saved_liters=water_saved_l,
        power_generated_kwh=power_kwh,
        crop_biomass_kg=lca_params.reference_biomass_kg,
    )

    # V5: Cooperative payback with dual OPEX and blended-finance subsidy
    coop_payback = lca_calc.calculate_cooperative_payback()
    logger.info(
        "[9/10] LCA — biomass: %.2f kg, CO2 avoided: %.2f kg, FU: %.2f, "
        "Coop payback: %.2f yr, NPV-10yr: %.0f USD (%s)",
        neb_results["effective_biomass_kg"],
        neb_results["net_benefit_co2_kg"],
        neb_results["functional_unit"],
        coop_payback["payback_yr"],
        coop_payback["npv_10yr_usd"],
        f"{_time.time() - _t_phase:.1f}s",
    )
    coop_payback["payback_yr"]  # kept for legacy HDF5 compatibility

    mc_results = lca_calc.monte_carlo_sensitivity(
        scenario="A",
        excitonic_yield_mean=physical_yield_npom,
        excitonic_yield_std=physical_yield_npom * 0.1,
        water_saved_liters_mean=water_saved_l,
        water_saved_liters_std=water_saved_l * 0.15,
        power_generated_kwh_mean=power_kwh,
        power_generated_kwh_std=power_kwh * 0.1,
        crop_biomass_kg_mean=lca_params.reference_biomass_kg,
        crop_biomass_kg_std=lca_params.reference_biomass_kg * 0.1,
        n_iterations=10000,
    )
    logger.info(
        "[9b/10] Monte Carlo NEB — CO2: %.2f±%.2f kg [5%%:%.2f, 95%%:%.2f] (%s)",
        mc_results["net_benefit_co2_kg"]["mean"],
        mc_results["net_benefit_co2_kg"]["std"],
        mc_results["net_benefit_co2_kg"]["p5"],
        mc_results["net_benefit_co2_kg"]["p95"],
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()

    coating = ZwitterionicCoating(config)
    annual_coating = coating.simulate_annual_cycle()
    logger.info(
        "[9c/10] Zwitterionic coating — %d reapp/yr, OPEX=%.0f USD/yr, avg coherence=%.2f (%s)",
        annual_coating["annual_reapplications"],
        annual_coating["annual_opex_usd"],
        annual_coating["avg_coherence_retention"],
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()

    gravimeter = QuantumGravimeter(config)
    irrigation_saving_m3 = water_saved_l * config.lca.footprint_m2 / 1000.0
    aquifer_result = gravimeter.estimate_aquifer_recharge(
        irrigation_saving_m3=irrigation_saving_m3, n_gravimeters=3
    )
    logger.info(
        "[9d/10] Quantum gravimetry — Δg=%.2e m/s², detectable=%s, SNR=%.1f (%s)",
        aquifer_result["mean_delta_g_ms2"],
        aquifer_result["detectable"],
        aquifer_result["signal_to_noise"],
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()

    qaoa = QAOAOptimizer(config)
    solar_profile = np.full(96, power_kwh / 24.0)
    qaoa_result = qaoa.solve(solar_profile)
    logger.info(
        "[9e/10] QAOA nexus — revenue=%.0f USD, utilization=%.1f%%, solar=%.1f kWh (%s)",
        qaoa_result["total_revenue_usd"],
        qaoa_result["utilization_fraction"] * 100,
        qaoa_result["total_solar_kwh"],
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()

    dsp = DataSovereigntyProtocol(config)
    dsp.record_provenance(
        data_hash=run_id,
        metadata={"trap_yield": float(trap_yield), "co2_kg": neb_results["net_benefit_co2_kg"]},
    )
    dsp.grant_consent("EU_floriculture_buyer")
    sovereignty_status = dsp.get_status()
    logger.info(
        "[9f/10] Data sovereignty — ledger=%d blocks, intact=%s, consent=%s (%s)",
        sovereignty_status["ledger_size"],
        sovereignty_status["ledger_intact"],
        sovereignty_status["consent_granted_parties"],
        f"{_time.time() - _t_phase:.1f}s",
    )
    _t_phase = _time.time()

    h5_file = os.path.join(_SCRIPT_DIR, config.output.dynamics_h5)
    os.makedirs(os.path.dirname(h5_file), exist_ok=True)
    populations = dm_array.diagonal(axis1=1, axis2=2).real
    cumulative_yield = 2.0 * gamma_rc * np.cumsum(trapped_pop) * dt_fs
    with h5py.File(h5_file, "w") as f:
        dyn = f.create_group("dynamics")
        dyn.create_dataset("populations", data=populations)
        dyn.create_dataset("trapped_pop", data=trapped_pop)
        dyn.create_dataset("rc_yield", data=cumulative_yield)
        dyn.attrs["run_id"] = run_id
        dyn.attrs["git_hash"] = git_hash
        dyn.attrs["timestamp"] = timestamp
        dyn.attrs["time_step_fs"] = dt_fs
    logger.info("[10/10] HDF5 saved: %s (%s)", h5_file, f"{_time.time() - _t_phase:.1f}s")
    _t_phase = _time.time()

    logger.info("[10/10] Rendering figures...")
    fig_gen = Paper2FigureGenerator(
        output_dir=os.path.join(_SCRIPT_DIR, config.output.graphics_dir)
    )
    fig1_path = fig_gen.plot_figure_1_quantum_dynamics(h5_file)
    logger.info("  → Figure 1: %s", fig1_path)

    fig2_path = fig_gen.plot_figure_2_sers_readout(sers_readout)
    logger.info("Figure 2 saved to: %s", fig2_path)

    neb_scenario_b = lca_calc.calculate_scenario_neb(
        scenario="B",
        excitonic_yield=physical_yield_npom * lca_params.scenario_b_yield_factor,
        water_saved_liters=water_saved_l * lca_params.scenario_b_water_factor,
        power_generated_kwh=power_kwh * lca_params.scenario_b_power_factor,
        crop_biomass_kg=lca_params.scenario_b_biomass_kg,
    )
    neb_scenario_c = lca_calc.calculate_scenario_neb(
        scenario="C",
        excitonic_yield=physical_yield_npom * lca_params.scenario_c_yield_factor,
        water_saved_liters=lca_params.scenario_c_water_liters,
        power_generated_kwh=lca_params.scenario_c_power_kwh,
        crop_biomass_kg=lca_params.scenario_c_biomass_kg,
    )
    fig3_path = fig_gen.plot_figure_3_lca_neb(neb_results, neb_scenario_b, neb_scenario_c)
    logger.info("Figure 3 saved to: %s", fig3_path)
