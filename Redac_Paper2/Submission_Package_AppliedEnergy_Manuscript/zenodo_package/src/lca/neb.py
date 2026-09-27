from pathlib import Path

import numpy as np

from ..config_loader import ConfigModel
from ..constants import (
    G_TO_KG,
    LCA_FOOTPRINT_A,
    LCA_FOOTPRINT_B,
    LCA_FOOTPRINT_C,
    LCA_MAX_PHYSICAL_YIELD,
    LCA_WATER_PUMPING_CARBON_FACTOR,
    QUANTUM_FERTILIZER_BOOST,
)

# Dual-band excitation filter (parameters.yaml spectral_filter block).
PASSBAND_CENTERS_NM = (750.0, 820.0)
PASSBANDWIDTH_CM = 100.0
# ASTM G173-03 global-tilt reference spectrum shipped with the framework.
_AM15G_CSV = (
    Path(__file__).resolve().parents[3]
    / "quantum_simulations_framework"
    / "data"
    / "input"
    / "ASTMG173.csv"
)
# Fallback integrals of that same file (band 10.236 W/m2, total 1000.4 W/m2,
# 280-1100 nm window 804.6 W/m2) used if the CSV is unavailable.
_FALLBACK = (0.0102, 0.0127, 10.236)


def passband_fraction(csv_path=None) -> tuple[float, float, float]:
    """Spectral cost of the two filter passbands.

    Integrates the ASTM G173-03 global-tilt spectrum over each
    ``PASSBAND_CENTERS_NM`` line (width = centre^2 * 100 cm^-1 * 1e-7, i.e.
    5.6 nm at 750 nm and 6.7 nm at 820 nm).

    Returns:
        ``(f_am15g, f_pv_window, band_irradiance_w_m2)`` where ``f_am15g``
        is the fraction of the full AM1.5G irradiance (1000.4 W/m2),
        ``f_pv_window`` the fraction of the 280-1100 nm harvestable window,
        and ``band_irradiance_w_m2`` the combined passband irradiance.
    """
    path = Path(_AM15G_CSV if csv_path is None else csv_path)
    if not path.exists():
        return _FALLBACK
    data = np.genfromtxt(path, delimiter=",", skip_header=2)
    wavelength_nm, global_tilt = data[:, 0], data[:, 2]
    band_irradiance = 0.0
    for centre_nm in PASSBAND_CENTERS_NM:
        half_width_nm = centre_nm**2 * PASSBANDWIDTH_CM * 1e-7 / 2.0
        mask = (wavelength_nm >= centre_nm - half_width_nm) & (
            wavelength_nm <= centre_nm + half_width_nm
        )
        band_irradiance += float(np.trapz(global_tilt[mask], wavelength_nm[mask]))
    total = float(np.trapz(global_tilt, wavelength_nm))
    window = (wavelength_nm >= 280.0) & (wavelength_nm <= 1100.0)
    window_total = float(np.trapz(global_tilt[window], wavelength_nm[window]))
    return (band_irradiance / total, band_irradiance / window_total, band_irradiance)


class NetEcologicalBenefit:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.grid_intensity = config.lca.carbon["grid_intensity_gco2_kwh"]

    def calculate_scenario_neb(
        self,
        scenario: str,
        excitonic_yield: float,
        water_saved_liters: float,
        power_generated_kwh: float,
        crop_biomass_kg: float,
        apply_fertilizer_boost: bool | None = None,
    ) -> dict:
        # Biostimulation boost (β_QF = 1.08) applies ONLY to Scenario A: the CQD
        # sentinel network that delivers the quantum fertiliser exists solely in
        # the quantum agrivoltaic configuration (see SI quantum-fertiliser).
        if apply_fertilizer_boost is None:
            apply_fertilizer_boost = scenario == "A"
        boost = QUANTUM_FERTILIZER_BOOST if apply_fertilizer_boost else 1.0
        safe_yield = min(excitonic_yield, LCA_MAX_PHYSICAL_YIELD)
        effective_biomass = crop_biomass_kg * (safe_yield / LCA_MAX_PHYSICAL_YIELD) * boost

        carbon_avoided_power = power_generated_kwh * (self.grid_intensity / G_TO_KG)
        carbon_avoided_water = water_saved_liters * LCA_WATER_PUMPING_CARBON_FACTOR

        if scenario == "A":
            footprint = LCA_FOOTPRINT_A
        elif scenario == "B":
            footprint = LCA_FOOTPRINT_B
        else:
            footprint = LCA_FOOTPRINT_C
            carbon_avoided_power = 0.0

        net_benefit = (carbon_avoided_power + carbon_avoided_water) - footprint

        return {
            "effective_biomass_kg": float(effective_biomass),
            "net_benefit_co2_kg": float(net_benefit),
            "functional_unit": float(power_generated_kwh * effective_biomass),
        }

    def calculate_cooperative_payback(
        self,
        capex: float | None = None,
        annual_revenue: float | None = None,
        annual_opex: float | None = None,
        training_opex: float | None = None,
        cleaning_opex: float | None = None,
        subsidy_rate: float | None = None,
        discount_rate: float | None = None,
        area_m2: float | None = None,
    ) -> dict:
        """
        V5: Compute cooperative financial metrics for the 500 m² micro-module
        with dual OPEX (training + cleaning) and blended-finance subsidy.

        Returns:
            dict with 'payback_yr', 'npv_10yr_usd', 'lcoe_usd_kwh',
            'net_revenue_usd_per_m2_yr', and effective CAPEX/OPEX values.
        """
        coop = self.config.lca.cooperative

        # --- Defaults from config ---
        capex = capex if capex is not None else self.config.lca.default_capex
        annual_revenue = (
            annual_revenue if annual_revenue is not None else self.config.lca.default_annual_revenue
        )
        annual_opex = (
            annual_opex if annual_opex is not None else self.config.lca.default_annual_opex
        )
        training_opex = (
            training_opex if training_opex is not None else coop.annual_training_opex_usd
        )
        cleaning_opex = (
            cleaning_opex if cleaning_opex is not None else coop.annual_cleaning_opex_usd
        )
        subsidy_rate = subsidy_rate if subsidy_rate is not None else coop.capex_subsidy_rate
        discount_rate = discount_rate if discount_rate is not None else coop.discount_rate
        area_m2 = area_m2 if area_m2 is not None else coop.area_m2

        # --- Boundary guards ---
        subsidy_rate = max(0.0, min(subsidy_rate, 1.0))
        discount_rate = max(discount_rate, -0.999)  # Prevent zero denominator in NPV

        # --- Core financial computation ---
        effective_capex = capex * (1.0 - subsidy_rate)  # Net of blended-finance grant
        total_annual_opex = annual_opex + training_opex + cleaning_opex  # Dual OPEX
        net_annual_cashflow = annual_revenue - total_annual_opex

        if net_annual_cashflow <= 0.0:
            payback_yr = float("inf")
        else:
            payback_yr = effective_capex / net_annual_cashflow

        # 10-year NPV using discounted cash flows
        npv_10yr = -effective_capex + sum(
            net_annual_cashflow / (1.0 + discount_rate) ** yr for yr in range(1, 11)
        )

        # LCOE proxy: effective_capex / (10-yr revenue) per m2
        lcoe_proxy = effective_capex / max(annual_revenue * 10, 1.0)

        net_revenue_per_m2 = net_annual_cashflow / max(area_m2, 1.0)

        return {
            "effective_capex_usd": float(effective_capex),
            "total_annual_opex_usd": float(total_annual_opex),
            "training_opex_usd": float(training_opex),
            "cleaning_opex_usd": float(cleaning_opex),
            "net_annual_cashflow_usd": float(net_annual_cashflow),
            "payback_yr": float(payback_yr),
            "npv_10yr_usd": float(npv_10yr),
            "lcoe_proxy": float(lcoe_proxy),
            "net_revenue_usd_per_m2_yr": float(net_revenue_per_m2),
            "area_m2": float(area_m2),
        }

    def monte_carlo_sensitivity(
        self,
        scenario: str,
        excitonic_yield_mean: float,
        excitonic_yield_std: float,
        water_saved_liters_mean: float,
        water_saved_liters_std: float,
        power_generated_kwh_mean: float,
        power_generated_kwh_std: float,
        crop_biomass_kg_mean: float,
        crop_biomass_kg_std: float,
        grid_intensity_std: float | None = None,
        footprint_std: float | None = None,
        capex_mean: float | None = None,
        capex_std: float | None = None,
        revenue_mean: float | None = None,
        revenue_std: float | None = None,
        n_iterations: int = 100000,
    ) -> dict:
        rng = np.random.default_rng(42)

        # Sample all inputs in parallel (vectorized)
        excitonic_yields = rng.normal(excitonic_yield_mean, excitonic_yield_std, n_iterations)
        water_saved = rng.normal(water_saved_liters_mean, water_saved_liters_std, n_iterations)
        power = rng.normal(power_generated_kwh_mean, power_generated_kwh_std, n_iterations)
        biomass = rng.normal(crop_biomass_kg_mean, crop_biomass_kg_std, n_iterations)

        # Add grid intensity uncertainty if provided
        if grid_intensity_std is not None and grid_intensity_std > 0.0:
            grid_values = rng.normal(self.grid_intensity, grid_intensity_std, n_iterations)
            grid_values = np.clip(grid_values, self.grid_intensity * 0.5, self.grid_intensity * 1.5)
        else:
            grid_values = np.full(n_iterations, self.grid_intensity)

        # Physical constraints
        excitonic_yields = np.clip(excitonic_yields, 0.0, LCA_MAX_PHYSICAL_YIELD)
        water_saved = np.clip(water_saved, 0.0, None)
        power = np.clip(power, 0.0, None)
        biomass = np.clip(biomass, 0.0, None)

        # Vectorized calculation. The biostimulation boost (β_QF = 1.08) applies
        # only to Scenario A (CQD sentinel delivery); Monte Carlo is only invoked
        # for the quantum scenario in the workflow.
        boost = QUANTUM_FERTILIZER_BOOST if scenario == "A" else 1.0
        safe_yield = np.minimum(excitonic_yields, LCA_MAX_PHYSICAL_YIELD)
        effective_biomass = biomass * (safe_yield / LCA_MAX_PHYSICAL_YIELD) * boost
        carbon_avoided_power = power * (grid_values / G_TO_KG)
        carbon_avoided_water = water_saved * LCA_WATER_PUMPING_CARBON_FACTOR

        if scenario == "A":
            footprint_base = LCA_FOOTPRINT_A
        elif scenario == "B":
            footprint_base = LCA_FOOTPRINT_B
        else:
            footprint_base = LCA_FOOTPRINT_C
            carbon_avoided_power = np.zeros_like(power)

        # Sample footprint uncertainty if provided
        if footprint_std is not None and footprint_std > 0.0:
            footprints = rng.normal(footprint_base, footprint_std, n_iterations)
            footprints = np.clip(footprints, footprint_base * 0.5, footprint_base * 1.5)
        else:
            footprints = np.full(n_iterations, footprint_base)

        net_benefit = (carbon_avoided_power + carbon_avoided_water) - footprints
        functional_unit = power * effective_biomass

        # Build summary statistics
        summary = {}
        stat_keys = [
            ("effective_biomass_kg", effective_biomass),
            ("net_benefit_co2_kg", net_benefit),
            ("functional_unit", functional_unit),
        ]

        # Optional economic block: payback/NPV uncertainty consistent with
        # calculate_cooperative_payback (same subsidy, OPEX, discount rate).
        if capex_mean is not None and revenue_mean is not None:
            coop = self.config.lca.cooperative
            opex_total = (
                self.config.lca.default_annual_opex
                + coop.annual_training_opex_usd
                + coop.annual_cleaning_opex_usd
            )
            capex_draws = np.clip(rng.normal(capex_mean, capex_std or 0.0, n_iterations), 0.0, None)
            revenue_draws = np.clip(
                rng.normal(revenue_mean, revenue_std or 0.0, n_iterations), 0.0, None
            )
            cashflow = revenue_draws - opex_total
            subsidy = max(0.0, min(coop.capex_subsidy_rate, 1.0))
            net_capex = capex_draws * (1.0 - subsidy)
            rate = max(coop.discount_rate, -0.999)
            annuity = sum(1.0 / (1.0 + rate) ** yr for yr in range(1, 11))
            payback = np.where(
                cashflow > 0.0, net_capex / np.where(cashflow > 0.0, cashflow, 1.0), np.inf
            )
            npv = cashflow * annuity - net_capex
            stat_keys.append(("payback_yr", payback))
            stat_keys.append(("npv_10yr_usd", npv))

        for key, arr in stat_keys:
            summary[key] = {
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr)),
                "p5": float(np.percentile(arr, 5)),
                "p25": float(np.percentile(arr, 25)),
                "p50": float(np.percentile(arr, 50)),
                "p75": float(np.percentile(arr, 75)),
                "p95": float(np.percentile(arr, 95)),
            }

        return summary
