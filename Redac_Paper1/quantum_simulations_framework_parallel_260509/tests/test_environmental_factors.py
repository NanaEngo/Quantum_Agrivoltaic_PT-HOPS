"""
test_environmental_factors.py — Tests for the EnvironmentalFactors model.
Focuses on temperature sweeps and physical coefficients.
"""
import sys
import numpy as np
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import get_test_logger
from models.environmental_factors import EnvironmentalFactors
from core.constants import ENVIRONMENTAL_T_REF, DEFAULT_PCE, DEFAULT_ETR
from reproducibility.main import load_and_validate_config

logger = get_test_logger("test_environmental_factors")

@pytest.fixture
def env_model():
    return EnvironmentalFactors()

@pytest.fixture
def config():
    return load_and_validate_config()

def test_temperature_sweep_range(env_model):
    """Verify that temperature sweeps handle the JPCL range correctly (285-310 K)."""
    temps = np.linspace(285, 310, 6)
    base_eff = DEFAULT_PCE

    opv_eff = env_model.temperature_effects_model(temps, base_eff, "opv")
    logger.info(f"OPV efficiency sweep: {opv_eff.round(4)}")
    assert len(opv_eff) == 6
    assert np.all(opv_eff <= base_eff)
    assert opv_eff[0] > opv_eff[-1], "Efficiency should decrease with temperature"

    psu_eff = env_model.temperature_effects_model(temps, base_eff, "psu")
    logger.info(f"PSU efficiency sweep: {psu_eff.round(4)}")
    assert psu_eff[0] > psu_eff[-1]

def test_dust_saturation(env_model):
    """Verify that dust accumulation saturates at self.dust_saturation_thickness."""
    time_days = np.linspace(0, 1000, 100)
    dust = env_model.dust_accumulation_model(time_days, initial_dust=0.0)
    logger.info(f"Dust: max={dust.max():.4f}, saturation_limit={env_model.dust_saturation_thickness:.4f}")
    assert np.max(dust) <= env_model.dust_saturation_thickness + 1e-6

def test_combined_effects_positivity(env_model):
    """Combined environmental effects must result in positive efficiencies."""
    time = np.array([1, 2, 3])
    temps = np.array([300, 310, 320])
    humidity = np.array([0.5, 0.6, 0.7])
    wind = np.array([5, 10, 15])

    pce, etr, _ = env_model.combined_environmental_effects(
        time, temps, humidity, wind, DEFAULT_PCE, DEFAULT_ETR
    )
    logger.info(f"Combined effects: PCE={pce}, ETR={etr}")
    assert np.all(pce >= 0)
    assert np.all(etr >= 0)
    assert np.all(pce <= DEFAULT_PCE + 1e-6)
    assert np.all(etr <= DEFAULT_ETR + 1e-6)

def test_reference_temperature_efficiency(env_model):
    """At reference temperature, efficiency should be the base efficiency."""
    T_ref = ENVIRONMENTAL_T_REF
    base_eff = DEFAULT_PCE
    eff = env_model.temperature_effects_model(np.array([T_ref]), base_eff, "opv")
    logger.info(f"Efficiency at T_ref={T_ref} K: {eff[0]:.6f} (expected ~{base_eff})")
    assert np.isclose(eff[0], base_eff, atol=1e-3)

if __name__ == "__main__":
    pytest.main([__file__])
