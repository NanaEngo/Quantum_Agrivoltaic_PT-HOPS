import sys
import numpy as np
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Duplicate import removed
from conftest import get_test_logger
from core.hamiltonian_factory import create_fmo_hamiltonian
from core.hops_simulator import HopsSimulator
from core.constants import (
    DEFAULT_TEMPERATURE,
    PULSE_FWHM,
    DEFAULT_TIME_LONG,
    MAE_THRESHOLD,
    POPS_REAL_THRESHOLD
)
from reproducibility.main import load_and_validate_config

logger = get_test_logger("test_physics_validation")

@pytest.fixture
def config():
    return load_and_validate_config()

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
    return np.linspace(0, DEFAULT_TIME_LONG, 501)

class TestPhysicsValidation:

    def test_dimer_trace_preservation(self, dimer_hamiltonian, t_long):
        """Σ ρ_ii(t) = 1.0 within numerical tolerance."""
        sim = HopsSimulator(dimer_hamiltonian, use_mesohops=False)
        psi0 = np.zeros(dimer_hamiltonian.shape[0], dtype=complex)
        psi0[0] = 1.0
        results = sim.simulate_dynamics(t_long, psi0, strict_mode=True)

        trace = np.sum(results["populations"], axis=1)
        max_dev = np.max(np.abs(trace - 1.0))
        logger.info(f"Dimer trace max deviation: {max_dev:.2e}")
        assert np.allclose(trace, 1.0, atol=MAE_THRESHOLD)

    def test_thermalization_limit(self, dimer_hamiltonian, t_long, config):
        """Boltzmann trend check."""
        temp = config['bath'].get('temperature', DEFAULT_TEMPERATURE)
        sim = HopsSimulator(dimer_hamiltonian, temperature=temp, use_mesohops=False)
        psi0 = np.ones(dimer_hamiltonian.shape[0], dtype=complex) / np.sqrt(dimer_hamiltonian.shape[0])
        results = sim.simulate_dynamics(t_long, psi0, strict_mode=True)

        final_pops = np.mean(results["populations"][-10:, :], axis=0)
        logger.info(f"Final populations (thermalization): {final_pops}")
        assert final_pops[0] < final_pops[1], "Higher energy site should be less populated"

    def test_gaussian_pulse_parameters(self):
        """Verify that pulse parameters are correctly stored."""
        H = np.eye(2) * 12000
        params = {
            "pulse_type": "Gaussian",
            "pulse_fwhm": PULSE_FWHM,
            "pulse_amplitude": 0.1,
            "pulse_center_freq": 12500.0
        }
        sim = HopsSimulator(H, **params)
        logger.info(f"Pulse params stored: {sim.system_param.get('PULSE_PARAMS', {})}")
        assert sim.system_param["PULSE_PARAMS"]["type"] == params["pulse_type"]
        assert sim.system_param["PULSE_PARAMS"]["fwhm"] == params["pulse_fwhm"]

    def test_positivity_conservation(self, dimer_hamiltonian, t_long):
        """Populations must remain non-negative."""
        sim = HopsSimulator(dimer_hamiltonian, use_mesohops=False)
        psi0 = np.zeros(dimer_hamiltonian.shape[0], dtype=complex)
        psi0[0] = 1.0
        results = sim.simulate_dynamics(t_long, psi0, strict_mode=True)
        min_pop = np.min(results["populations"])
        logger.info(f"Min population value: {min_pop:.2e}")
        assert min_pop >= -1e-6

    def test_high_temperature_decoherence(self, dimer_hamiltonian):
        """At very high T, coherences should decay faster."""
        t = np.linspace(0, 500, 100)
        n_sites = dimer_hamiltonian.shape[0]
        psi0 = np.ones(n_sites, dtype=complex) / np.sqrt(n_sites)

        sim_low = HopsSimulator(dimer_hamiltonian, temperature=10.0, use_mesohops=False)
        sim_high = HopsSimulator(dimer_hamiltonian, temperature=1000.0, use_mesohops=False)

        res_low = sim_low.simulate_dynamics(t, psi0, strict_mode=True)
        res_high = sim_high.simulate_dynamics(t, psi0, strict_mode=True)

        coh_low = np.sum(res_low["coherences"])
        coh_high = np.sum(res_high["coherences"])
        logger.info(f"Coherence sum: T=10K → {coh_low:.4f}, T=1000K → {coh_high:.4f}")
        logger.info(f"Simulator used: {res_low.get('simulator', 'Unknown')}")
        assert coh_high < coh_low

if __name__ == "__main__":
    pytest.main([__file__])
