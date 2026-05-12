import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import get_test_logger
from src.core.constants import FMO_COUPLINGS, FMO_SITE_ENERGIES_7, FMO_SITE_ENERGIES_8
from src.core.hamiltonian_factory import create_fmo_hamiltonian
from src.core.hops_simulator import HopsSimulator
from reproducibility.main import load_and_validate_config

logger = get_test_logger("test_core")

@pytest.fixture
def config():
    return load_and_validate_config()

def test_constants_validity(config):
    """Verify that core constants are correctly defined and have expected shapes."""
    assert len(FMO_SITE_ENERGIES_7) > 0
    assert isinstance(FMO_COUPLINGS, dict)
    temp = config['bath'].get('temperature', 295.0)
    logger.info(f"Temperature from config: {temp} K")
    assert 270 < temp < 320

def test_hamiltonian_factory():
    """Verify that the Hamiltonian factory generates valid FMO matrices."""
    H, energies = create_fmo_hamiltonian(include_reaction_center=False)
    n = H.shape[0]
    logger.info(f"FMO Hamiltonian shape: {H.shape}, Hermitian: {np.allclose(H, H.conj().T)}")
    assert H.shape == (n, n)
    assert np.allclose(np.diag(H), energies)
    assert np.allclose(H, H.conj().T)

    H8, e8 = create_fmo_hamiltonian(include_reaction_center=True)
    logger.info(f"FMO+RC Hamiltonian shape: {H8.shape}")
    assert H8.shape == (H8.shape[0], H8.shape[0])

def test_hops_simulator_initialization(config):
    """Test HopsSimulator initialization and fallback logic."""
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    temp = config['bath'].get('temperature', 295.0)
    simulator = HopsSimulator(H, temperature=temp, use_mesohops=False)
    logger.info(f"HopsSimulator initialized: T={simulator.temperature} K, mesohops={simulator.use_mesohops}")
    assert simulator.temperature == temp
    assert not simulator.use_mesohops

def test_hops_simulator_simulation_stub():
    """Test a basic simulation call (even if stubbed/failed in environment)."""
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    simulator = HopsSimulator(H, use_mesohops=False)

    time_points = np.linspace(0, 100, 10)
    psi0 = np.zeros(H.shape[0], dtype=complex)
    psi0[0] = 1.0

    results = simulator.simulate_dynamics(time_points, psi0)
    logger.info(f"Simulation result keys: {list(results.keys())}, pop shape: {results['populations'].shape}")
    assert isinstance(results, dict)
    assert "t_axis" in results
    assert "populations" in results

if __name__ == "__main__":
    pytest.main([__file__])
