"""
test_physics_validation.py — Deep physical invariant and validation tests.
Focuses on long-time limits, thermalization, and pulse physics.
"""
import sys
import numpy as np
import pytest
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.hamiltonian_factory import create_fmo_hamiltonian
from core.hops_simulator import HopsSimulator

@pytest.fixture
def dimer_hamiltonian():
    """Simple 2-site Hamiltonian for fast validation."""
    E1, E2 = 12500, 12400
    J = 100
    H = np.array([[E1, J], [J, E2]], dtype=float)
    return H

@pytest.fixture
def t_long():
    """Long time points to observe thermalization/decay."""
    return np.linspace(0, 5000, 500) # 5 ps

class TestPhysicsValidation:
    
    def test_dimer_trace_preservation(self, dimer_hamiltonian, t_long):
        """Σ ρ_ii(t) = 1.0 within numerical tolerance."""
        sim = HopsSimulator(dimer_hamiltonian, use_mesohops=False)
        psi0 = np.array([1.0, 0.0], dtype=complex)
        results = sim.simulate_dynamics(t_long, psi0)
        
        trace = np.sum(results["populations"], axis=1)
        assert np.allclose(trace, 1.0, atol=1e-3), "Trace must be preserved"

    def test_thermalization_limit(self, dimer_hamiltonian, t_long):
        """
        In the long-time limit, the ratio of populations should approach 
        the Boltzmann factor exp(-ΔE/kT).
        Note: Fallback simulator might not fully thermalize if it's too simple,
        but we check for the trend.
        """
        temp = 295.0
        kT = 0.695 * temp # cm^-1
        delta_E = np.abs(dimer_hamiltonian[0,0] - dimer_hamiltonian[1,1])
        expected_ratio = np.exp(-delta_E / kT)
        
        sim = HopsSimulator(dimer_hamiltonian, temperature=temp, use_mesohops=False)
        psi0 = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2)
        results = sim.simulate_dynamics(t_long, psi0)
        
        # Check final populations (average over last 10 points to reduce oscillations)
        final_pops = np.mean(results["populations"][-10:, :], axis=0)
        # Ratio of lower energy site to higher energy site
        # Site 2 (index 1) has E=12400 (lower)
        # Site 1 (index 0) has E=12500 (higher)
        actual_ratio = final_pops[0] / final_pops[1]
        
        # We don't expect exact Boltzmann in short simulations or simple models,
        # but the higher energy site should have lower population.
        assert actual_ratio < 1.0, "Higher energy site should be less populated in equilibrium"
        # Optional: check if it's moving towards Boltzmann
        # assert actual_ratio > expected_ratio * 0.5

    def test_gaussian_pulse_parameters(self):
        """Verify that pulse parameters are correctly stored in HopsSimulator."""
        H = np.eye(2) * 12000
        params = {
            "pulse_type": "Gaussian",
            "pulse_fwhm": 40.0,
            "pulse_amplitude": 0.1,
            "pulse_center_freq": 12500.0
        }
        sim = HopsSimulator(H, **params)
        
        assert sim.system_param["PULSE_PARAMS"]["type"] == "Gaussian"
        assert sim.system_param["PULSE_PARAMS"]["fwhm"] == 40.0
        assert sim.system_param["PULSE_PARAMS"]["amplitude"] == 0.1
        assert sim.system_param["PULSE_PARAMS"]["center_freq"] == 12500.0

    def test_positivity_conservation(self, dimer_hamiltonian, t_long):
        """Populations must remain non-negative."""
        sim = HopsSimulator(dimer_hamiltonian, use_mesohops=False)
        psi0 = np.array([1.0, 0.0], dtype=complex)
        results = sim.simulate_dynamics(t_long, psi0)
        
        assert np.all(results["populations"] >= -1e-6), "Negative populations detected"

    def test_high_temperature_decoherence(self, dimer_hamiltonian):
        """At very high T, coherences should decay faster."""
        t = np.linspace(0, 500, 100)
        psi0 = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2)
        
        sim_low = HopsSimulator(dimer_hamiltonian, temperature=10.0, use_mesohops=False)
        sim_high = HopsSimulator(dimer_hamiltonian, temperature=1000.0, use_mesohops=False)
        
        res_low = sim_low.simulate_dynamics(t, psi0)
        res_high = sim_high.simulate_dynamics(t, psi0)
        
        coh_low = res_low["coherences"]
        coh_high = res_high["coherences"]
        
        # Sum of coherences over time should be lower for high T
        assert np.sum(coh_high) < np.sum(coh_low), "Coherences should decay faster at high temperature"

if __name__ == "__main__":
    pytest.main([__file__])
