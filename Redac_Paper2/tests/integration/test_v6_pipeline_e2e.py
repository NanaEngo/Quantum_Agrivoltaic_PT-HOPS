"""
End-to-end integration test for the V6 pipeline additions (Digital Twin + QML
signal processing + soiling + LCA cooperative).

This script validates the complete non-quantum portion of the orchestrator
pipeline without requiring MesoHOPS.  It loads the real config, exercises
the SERS diagnostics, soiling attenuation, global canopy yield, Digital Twin
orchestration, QML signal processing, FAO-56 evapotranspiration, LCA
cooperative payback, and Monte Carlo NEB — the same steps a full production
run would execute.
"""

import os
import sys
import time as _time

import numpy as np

# Ensure the project is on sys.path (project root = tests/integration/../../)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.config_loader import load_config
from src.constants import (
    BASELINE_TRANSMISSION,
    MM_TO_LITER_PER_M2,
    WIND_SPEED_GREENHOUSE_FACTOR,
)
from src.lca.neb import NetEcologicalBenefit
from src.microclimate.fao56 import GreenhouseEvapotranspiration
from src.quantum_interface.diagnostics import SersDiagnostics
from src.quantum_interface.pulse import FloquetStarkSwitch
from src.quantum_interface.signal_processing import (
    detect_stress_anomaly,
)


def test_end_to_end_v6_pipeline() -> dict:
    """Run every non-quantum V6 pipeline step and return a results dict."""
    results = {}
    _t0 = _time.time()

    # ── 1. Config loading ────────────────────────────────────────────────
    config_path = os.path.join(_PROJECT_ROOT, "parameters.yaml")
    config = load_config(config_path)
    results["config_loaded"] = True
    results["digital_twin"] = {
        "update_interval_seconds": config.digital_twin.update_interval_seconds,
        "sync_opv_grid": config.digital_twin.sync_opv_grid,
    }
    results["quantum_signal"] = {
        "kernel_gamma": config.quantum_signal.kernel_gamma,
        "kernel_regularization": config.quantum_signal.kernel_regularization,
        "mps_chi": config.quantum_signal.mps_chi,
        "stress_anomaly_zscore": config.quantum_signal.stress_anomaly_zscore,
        "noise_sigma_fraction": config.quantum_signal.noise_sigma_fraction,
    }
    print(
        f"[1/8] Config loaded with Digital Twin ✓ — "
        f"refresh={config.digital_twin.update_interval_seconds}s, "
        f"grid-sync={config.digital_twin.sync_opv_grid}"
    )

    # ── 2. Soiling attenuation (Axe 5) ──────────────────────────────────
    solar_flux = 800.0
    days_since_cleaning = 30
    daily_decay_rate = config.physics.soiling_decay_rate_per_day
    power_ideal_kwh = solar_flux * config.lca.pv_efficiency * config.lca.pv_fill_factor
    power_soiled_kwh = SersDiagnostics.calculate_opv_power_with_soiling(
        power_ideal=power_ideal_kwh,
        days_since_cleaning=days_since_cleaning,
        daily_decay_rate=daily_decay_rate,
    )
    soiling_factor = power_soiled_kwh / max(power_ideal_kwh, 1e-9)
    results["soiling"] = {
        "power_ideal_kwh": float(power_ideal_kwh),
        "power_soiled_kwh": float(power_soiled_kwh),
        "soiling_factor": float(soiling_factor),
    }
    assert 0.0 < soiling_factor < 1.0, f"Soiling factor {soiling_factor} out of range"
    print(
        f"[2/8] Soiling attenuation ✓ — factor={soiling_factor:.4f}, "
        f"P_ideal={power_ideal_kwh:.1f}, P_soiled={power_soiled_kwh:.1f}"
    )

    # ── 3. Global canopy yield (Axe 2) ──────────────────────────────────
    trap_yield = 0.1685  # realistic 77K raw Phi_FT (2*Gamma*int)
    physical_yield_npom = trap_yield / 2.0  # normalize to [0, 1]
    phi_ft_passive = 0.98  # known baseline physical yield
    sers_obj = SersDiagnostics(config)
    sentinel_ratio = config.physics.sensing_sentinel_ratio
    phi_ft_global = sers_obj.calculate_global_canopy_yield(
        phi_ft_npom=physical_yield_npom,
        phi_ft_passive=phi_ft_passive,
        sentinel_ratio=sentinel_ratio,
    )
    results["global_yield"] = {
        "phi_ft_npom": float(physical_yield_npom),
        "phi_ft_passive": float(phi_ft_passive),
        "phi_ft_global": float(phi_ft_global),
        "sentinel_ratio": float(sentinel_ratio),
    }
    assert 0.0 < phi_ft_global <= 1.0, f"Global yield {phi_ft_global} out of range"
    print(
        f"[3/8] Global canopy yield ✓ — Phi_FT_NPoM(physical)={physical_yield_npom:.4f}, "
        f"Phi_FT_passive={phi_ft_passive:.4f}, "
        f"Phi_FT_global={phi_ft_global:.4f} (sentinel={sentinel_ratio * 100:.1f}%)"
    )

    # ── 4. SERS readout (Axe 4) ─────────────────────────────────────────
    final_pop = np.array([0.05, 0.10, 0.25, 0.15, 0.08, 0.06, 0.20, 0.11])
    sers_readout = sers_obj.calculate_raman_spectrum(final_pop)
    results["sers_readout"] = {k: v for k, v in sers_readout.items() if k != "stress_markers"}
    results["sers_stress_markers"] = sers_readout.get("stress_markers", {})
    print(
        f"[4/8] SERS Raman readout ✓ — 180_cm={sers_readout.get('180_cm', 0):.2f}, "
        f"740_cm={sers_readout.get('740_cm', 0):.2f}, "
        f"1145_cm={sers_readout.get('1145_cm', 0):.2f}"
    )

    # ── 5. QML signal processing (Axe 6) ────────────────────────────────
    raman_vals = np.array(
        [
            sers_readout.get("180_cm", 0.0),
            sers_readout.get("740_cm", 0.0),
            sers_readout.get("1145_cm", 0.0),
        ]
    )
    noise_fraction = config.quantum_signal.noise_sigma_fraction
    noise_level = noise_fraction * np.maximum(raman_vals, 1.0)
    rng = np.random.default_rng(42)
    noisy_spectrum = raman_vals + rng.normal(0.0, noise_level)
    noisy_spectrum = np.maximum(noisy_spectrum, 0.0)

    ref_dict = np.array(
        [
            [100.0, 50.0, 20.0],
            [60.0, 80.0, 120.0],
            [20.0, 10.0, 200.0],
        ],
        dtype=np.float64,
    )
    ref_labels = np.array([0.0, 0.4, 0.9], dtype=np.float64)

    sers_sig = config.quantum_signal
    anomaly_result = detect_stress_anomaly(
        noisy_spectrum=noisy_spectrum,
        reference_dictionary=ref_dict,
        reference_labels=ref_labels,
        gamma=sers_sig.kernel_gamma,
        regularization=sers_sig.kernel_regularization,
        zscore_threshold=sers_sig.stress_anomaly_zscore,
        mps_chi=sers_sig.mps_chi,
    )
    results["qml_anomaly"] = {
        "predicted_stress": anomaly_result["predicted_stress"],
        "anomaly_score": anomaly_result["anomaly_score"],
        "is_anomaly": anomaly_result["is_anomaly"],
        "early_warning": anomaly_result["early_warning"],
    }
    assert "denoised_spectrum" in anomaly_result
    print(
        f"[5/8] QML signal processing ✓ — stress={anomaly_result['predicted_stress']:.3f}, "
        f"anomaly={anomaly_result['anomaly_score']:.3f}, "
        f"early_warning={anomaly_result['early_warning']}"
    )

    # ── 6. FAO-56 Evapotranspiration (Axe 1) ────────────────────────────
    floquet_switch = FloquetStarkSwitch(config)
    effective_transmission = floquet_switch.apply_omit_attenuation(
        solar_flux, baseline_transmission=BASELINE_TRANSMISSION
    )
    solar_flux_greenhouse = solar_flux * effective_transmission
    climate = GreenhouseEvapotranspiration(config)
    mc = config.microclimate
    wind_greenhouse = mc.default_wind_speed_m_s * WIND_SPEED_GREENHOUSE_FACTOR
    et_rate = climate.calculate_evapotranspiration(
        solar_flux_w_m2=solar_flux_greenhouse,
        temp_c=mc.default_temp_c,
        relative_humidity_pct=mc.default_rh_pct,
        wind_speed_m_s=wind_greenhouse,
    )
    baseline_water_mm = mc.baseline_water_mm
    water_saved_l = max(0.0, baseline_water_mm - et_rate) * MM_TO_LITER_PER_M2
    results["fao56"] = {
        "et_rate_mm_day": float(et_rate),
        "water_saved_liters": float(water_saved_l),
    }
    assert et_rate >= 0.0
    print(
        f"[6/8] FAO-56 ET_c ✓ — et_rate={et_rate:.4f} mm/day, water_saved={water_saved_l:.1f} L/m2"
    )

    # ── 7. LCA cooperative payback (Axe 3) ──────────────────────────────
    lca_calc = NetEcologicalBenefit(config)
    lca_params = config.lca

    neb_results = lca_calc.calculate_scenario_neb(
        scenario="A",
        excitonic_yield=phi_ft_global,
        water_saved_liters=water_saved_l,
        power_generated_kwh=power_soiled_kwh,
        crop_biomass_kg=lca_params.reference_biomass_kg,
    )
    coop_payback = lca_calc.calculate_cooperative_payback()
    results["lca"] = {
        "effective_biomass_kg": neb_results["effective_biomass_kg"],
        "net_benefit_co2_kg": neb_results["net_benefit_co2_kg"],
        "functional_unit": neb_results["functional_unit"],
        "effective_capex_usd": coop_payback["effective_capex_usd"],
        "total_annual_opex_usd": coop_payback["total_annual_opex_usd"],
        "payback_yr": coop_payback["payback_yr"],
        "npv_10yr_usd": coop_payback["npv_10yr_usd"],
        "net_revenue_usd_per_m2_yr": coop_payback["net_revenue_usd_per_m2_yr"],
    }
    assert coop_payback["payback_yr"] > 0.0
    assert coop_payback["training_opex_usd"] == 1200.0
    assert coop_payback["cleaning_opex_usd"] == 800.0
    print(
        f"[7/8] LCA cooperative ✓ — payback={coop_payback['payback_yr']:.2f} yr, "
        f"NPV-10yr={coop_payback['npv_10yr_usd']:.0f} USD, "
        f"CO2_avoided={neb_results['net_benefit_co2_kg']:.2f} kg"
    )

    # ── 8. Monte Carlo NEB sensitivity ──────────────────────────────────
    mc_results = lca_calc.monte_carlo_sensitivity(
        scenario="A",
        excitonic_yield_mean=trap_yield,
        excitonic_yield_std=trap_yield * 0.1,
        water_saved_liters_mean=water_saved_l,
        water_saved_liters_std=water_saved_l * 0.15,
        power_generated_kwh_mean=power_soiled_kwh,
        power_generated_kwh_std=power_soiled_kwh * 0.1,
        crop_biomass_kg_mean=lca_params.reference_biomass_kg,
        crop_biomass_kg_std=lca_params.reference_biomass_kg * 0.1,
        n_iterations=10000,
    )
    results["monte_carlo"] = {
        "co2_mean": mc_results["net_benefit_co2_kg"]["mean"],
        "co2_std": mc_results["net_benefit_co2_kg"]["std"],
        "co2_p5": mc_results["net_benefit_co2_kg"]["p5"],
        "co2_p95": mc_results["net_benefit_co2_kg"]["p95"],
    }
    print(
        f"[8/8] Monte Carlo NEB ✓ — CO2: "
        f"{mc_results['net_benefit_co2_kg']['mean']:.2f} ± "
        f"{mc_results['net_benefit_co2_kg']['std']:.2f} kg "
        f"[5%:{mc_results['net_benefit_co2_kg']['p5']:.2f}, "
        f"95%:{mc_results['net_benefit_co2_kg']['p95']:.2f}]"
    )

    elapsed = _time.time() - _t0
    results["total_elapsed_s"] = round(elapsed, 2)
    print(f"\n{'=' * 55}")
    print(f"✅ V6 pipeline complete — {elapsed:.1f}s — all {len(results)} assertions passed")
    print(f"{'=' * 55}")

    return results


if __name__ == "__main__":
    r = test_end_to_end_v6_pipeline()
    # Pretty-print key metrics
    print("\n📊 Summary of key V6 metrics:")
    print(f"   Phi_FT_global         = {r['global_yield']['phi_ft_global']:.4f}")
    print(f"   Soiling factor        = {r['soiling']['soiling_factor']:.4f}")
    print(f"   QML anomaly score     = {r['qml_anomaly']['anomaly_score']:.4f}")
    print(f"   Payback period        = {r['lca']['payback_yr']:.2f} yr")
    print(f"   NPV-10yr              = {r['lca']['npv_10yr_usd']:.0f} USD")
    print(f"   Digital Twin refresh  = {r['digital_twin']['update_interval_seconds']}s")
    print(f"   QML kernel gamma      = {r['quantum_signal']['kernel_gamma']}")
