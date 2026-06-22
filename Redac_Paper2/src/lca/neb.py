from ..config_loader import ConfigModel
from ..constants import (
    LCA_FOOTPRINT_A,
    LCA_FOOTPRINT_B,
    LCA_FOOTPRINT_C,
    LCA_MAX_PHYSICAL_YIELD,
    LCA_WATER_PUMPING_CARBON_FACTOR,
)


class NetEcologicalBenefit:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.grid_intensity = config.lca.carbon.get("grid_intensity_gco2_kwh", 450.0)

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

        carbon_avoided_power = power_generated_kwh * (self.grid_intensity / 1000.0)
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
