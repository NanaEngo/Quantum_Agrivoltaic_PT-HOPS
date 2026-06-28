import os

from src.config_loader import load_config
from src.lca.database import AmortizationAnalysis
from src.lca.neb import NetEcologicalBenefit
from src.microclimate.fao56 import GreenhouseEvapotranspiration


def test_greenhouse_evapotranspiration():
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    climate = GreenhouseEvapotranspiration(config)
    et = climate.calculate_evapotranspiration(600.0, 25.0, 60.0, 2.0)
    assert et > 0.0


def test_fao56_absolute_zero_guard():
    """E-1: Division by zero when temp_c = -273.15°C should return 0.0."""
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    climate = GreenhouseEvapotranspiration(config)
    # Absolute zero exactly triggers the division-by-zero edge case
    et_abs_zero = climate.calculate_evapotranspiration(600.0, -273.15, 60.0, 2.0)
    assert et_abs_zero == 0.0

    # Even colder (unphysical) should also be guarded
    et_colder = climate.calculate_evapotranspiration(600.0, -300.0, 60.0, 2.0)
    assert et_colder == 0.0


def test_fao56_humidity_clamping():
    """Humidity > 100% should be clamped to 100% without raising errors."""
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    climate = GreenhouseEvapotranspiration(config)
    et_at100 = climate.calculate_evapotranspiration(600.0, 25.0, 100.0, 2.0)
    et_over100 = climate.calculate_evapotranspiration(600.0, 25.0, 150.0, 2.0)
    # Both 100% and 150% clamp to 100% → identical ET
    assert et_over100 == et_at100
    # Negative humidity should also be clamped to 0%
    et_neg = climate.calculate_evapotranspiration(600.0, 25.0, -10.0, 2.0)
    assert et_neg >= 0.0


def test_net_ecological_benefit():
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    neb = NetEcologicalBenefit(config)
    # Use yield = 0.95 (capped) to verify capping doesn't produce unphysical >100% biomass
    results = neb.calculate_scenario_neb("A", 0.95, 1000.0, 50.0, 10.0)
    assert results["effective_biomass_kg"] == 10.8  # 10.0 * 1.08 boost
    assert results["net_benefit_co2_kg"] > 0.0
    assert results["functional_unit"] > 0.0

    # Verify capping behavior: yield > 0.95 should not exceed 100% biomass
    results_capped = neb.calculate_scenario_neb("A", 1.0, 1000.0, 50.0, 10.0)
    assert results_capped["effective_biomass_kg"] == 10.8  # capped at 10.8
    assert results_capped["effective_biomass_kg"] <= 10.8  # never exceed reference boosted


def test_amortization_analysis():
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    analysis = AmortizationAnalysis(config)
    payback = analysis.calculate_payback_years(10000.0, 2000.0, 0.0)
    # net_capex = 10000 * (1 - 0.3) = 7000
    # capex_per_member = 7000 / 5 = 1400
    # net_annual_revenue_per_member = (2000 - 0) / 5 = 400
    # payback = 1400 / 400 = 3.5 years
    assert payback == 3.5
