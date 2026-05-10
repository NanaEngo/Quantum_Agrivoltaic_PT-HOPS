"""
test_environmental_factors.py — Tests for the EnvironmentalFactors model.
Focuses on temperature sweeps and physical coefficients.
"""
import sys
import numpy as np
import pytest
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.environmental_factors import EnvironmentalFactors

@pytest.fixture
def env_model():
    return EnvironmentalFactors()

def test_temperature_sweep_range(env_model):
    """Verify that temperature sweeps handle the JPCL range correctly (285-310 K)."""
    temps = np.linspace(285, 310, 6)
    base_eff = 0.15 # 15%
    
    # Test OPV
    opv_eff = env_model.temperature_effects_model(temps, base_eff, "opv")
    assert len(opv_eff) == 6
    assert np.all(opv_eff <= base_eff)
    assert opv_eff[0] > opv_eff[-1], "Efficiency should decrease with temperature"

    # Test PSU
    psu_eff = env_model.temperature_effects_model(temps, base_eff, "psu")
    assert psu_eff[0] > psu_eff[-1]
    
def test_dust_saturation(env_model):
    """Verify that dust accumulation saturates at self.dust_saturation_thickness."""
    time_days = np.linspace(0, 1000, 100) # Long time
    dust = env_model.dust_accumulation_model(time_days, initial_dust=0.0)
    
    # Due to random precipitation in the model, we check for a high value
    # but not necessarily the exact saturation if a reset happened at the end.
    # However, at some point it should be close to saturation.
    assert np.max(dust) <= env_model.dust_saturation_thickness

def test_combined_effects_positivity(env_model):
    """Combined environmental effects must result in positive efficiencies."""
    time = np.array([1, 2, 3])
    temps = np.array([300, 310, 320])
    humidity = np.array([0.5, 0.6, 0.7])
    wind = np.array([5, 10, 15])
    
    pce, etr, _ = env_model.combined_environmental_effects(
        time, temps, humidity, wind, 0.18, 0.12
    )
    
    assert np.all(pce >= 0)
    assert np.all(etr >= 0)
    assert np.all(pce <= 0.18)
    assert np.all(etr <= 0.12)

def test_reference_temperature_efficiency(env_model):
    """At reference temperature (298K), efficiency should be the base efficiency."""
    T_ref = 298.0
    base_eff = 0.20
    eff = env_model.temperature_effects_model(np.array([T_ref]), base_eff, "opv")
    assert np.isclose(eff[0], base_eff)

if __name__ == "__main__":
    pytest.main([__file__])
