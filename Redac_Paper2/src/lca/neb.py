import numpy as np

from ..config_loader import ConfigModel
from ..constants import (
    G_TO_KG,
    LCA_FOOTPRINT_A,
    LCA_FOOTPRINT_B,
    LCA_FOOTPRINT_C,
    LCA_MAX_PHYSICAL_YIELD,
    LCA_WATER_PUMPING_CARBON_FACTOR,
)


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
    ) -> dict:
        safe_yield = min(excitonic_yield, LCA_MAX_PHYSICAL_YIELD)
        effective_biomass = crop_biomass_kg * (safe_yield / LCA_MAX_PHYSICAL_YIELD)

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

        # Vectorized calculation
        safe_yield = np.minimum(excitonic_yields, LCA_MAX_PHYSICAL_YIELD)
        effective_biomass = biomass * (safe_yield / LCA_MAX_PHYSICAL_YIELD)
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
        for key, arr in [
            ("effective_biomass_kg", effective_biomass),
            ("net_benefit_co2_kg", net_benefit),
            ("functional_unit", functional_unit),
        ]:
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
