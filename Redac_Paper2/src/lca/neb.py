from ..config_loader import ConfigModel

# LCA physical constants
# Maximum physically plausible excitonic yield (prevents > 100% biomass conversion)
MAX_PHYSICAL_YIELD = 0.95
# Carbon emission factor for water pumping (kg CO2e per liter)
WATER_PUMPING_CARBON_FACTOR = 0.000298
# Manufacturing carbon footprint (kg CO2e / m2 / yr) per scenario
# Scenario A: Quantum OPV with graphene/plasmonic materials (higher footprint)
FOOTPRINT_SCENARIO_A = 8.5
# Scenario B: Static shading PV (standard)
FOOTPRINT_SCENARIO_B = 5.0
# Scenario C: Open field (no manufacturing)
FOOTPRINT_SCENARIO_C = 0.0


class NetEcologicalBenefit:
    """
    Computes LCA metrics and Net Ecological Benefit (NEB) using a combined functional unit
    (kWh * kg_crop / m2 * yr) to compare Scenarios A, B, and C.
    """

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
        """
        Calculates Net Ecological Benefit (NEB) in kg CO2e avoided per m2 per year.
        NEB = (Power generated * grid carbon offset) + (Water saved offset) - (Manufacturing footprint)
        """
        # Excitonic yield acts as a direct multiplier on crop biomass harvested
        # Cap yield to prevent unphysical biomass > 100% of reference
        safe_yield = min(excitonic_yield, MAX_PHYSICAL_YIELD)
        effective_biomass = crop_biomass_kg * (safe_yield / MAX_PHYSICAL_YIELD)

        # Carbon credits
        carbon_avoided_power = power_generated_kwh * (
            self.grid_intensity / 1000.0
        )  # kg CO2
        carbon_avoided_water = (
            water_saved_liters * WATER_PUMPING_CARBON_FACTOR
        )  # standard pumping carbon cost per liter

        # Manufacturing footprint penalty per scenario
        if scenario == "A":  # Quantum OPV selective
            footprint = FOOTPRINT_SCENARIO_A
        elif scenario == "B":  # Static shading PV
            footprint = FOOTPRINT_SCENARIO_B
        else:  # Scenario C: open field
            footprint = FOOTPRINT_SCENARIO_C
            carbon_avoided_power = 0.0

        net_benefit = (carbon_avoided_power + carbon_avoided_water) - footprint

        return {
            "effective_biomass_kg": float(effective_biomass),
            "net_benefit_co2_kg": float(net_benefit),
            "functional_unit": float(power_generated_kwh * effective_biomass),
        }
