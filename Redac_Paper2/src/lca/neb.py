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
        n_iterations: int = 10000,
    ) -> dict:
        rng = np.random.default_rng(42)

        excitonic_yields = rng.normal(excitonic_yield_mean, excitonic_yield_std, n_iterations)
        water_saved = rng.normal(water_saved_liters_mean, water_saved_liters_std, n_iterations)
        power = rng.normal(power_generated_kwh_mean, power_generated_kwh_std, n_iterations)
        biomass = rng.normal(crop_biomass_kg_mean, crop_biomass_kg_std, n_iterations)

        excitonic_yields = np.clip(excitonic_yields, 0.0, LCA_MAX_PHYSICAL_YIELD)
        water_saved = np.clip(water_saved, 0.0, None)
        power = np.clip(power, 0.0, None)
        biomass = np.clip(biomass, 0.0, None)

        results = {
            "effective_biomass_kg": [],
            "net_benefit_co2_kg": [],
            "functional_unit": [],
        }

        for i in range(n_iterations):
            r = self.calculate_scenario_neb(
                scenario=scenario,
                excitonic_yield=excitonic_yields[i],
                water_saved_liters=water_saved[i],
                power_generated_kwh=power[i],
                crop_biomass_kg=biomass[i],
            )
            results["effective_biomass_kg"].append(r["effective_biomass_kg"])
            results["net_benefit_co2_kg"].append(r["net_benefit_co2_kg"])
            results["functional_unit"].append(r["functional_unit"])

        summary = {}
        for key, vals in results.items():
            arr = np.array(vals)
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
