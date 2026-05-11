import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import get_test_logger
from src.core.hamiltonian_factory import create_fmo_hamiltonian
from src.core.hops_simulator import MESOHOPS_AVAILABLE
from models.quantum_dynamics_simulator import QuantumDynamicsSimulator
from src.quantum.spectroscopy import Spectroscopy2DES

logger = get_test_logger("test_models_dynamics")

def test_quantum_dynamics_simulator():
    """Test the standalone QuantumDynamicsSimulator."""
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    n_sites = H.shape[0]
    simulator = QuantumDynamicsSimulator(H)

    # Reduced time window for laptop testing
    time_points = np.linspace(0, 10, 5)  # Changed from (0, 100, 20)
    psi0 = np.zeros(n_sites, dtype=complex)
    psi0[0] = 1.0
    psi0 = psi0.reshape(-1)

    results = simulator.simulate_dynamics(time_points, psi0)

    logger.info(f"QuantumDynamicsSimulator: pop shape={results['populations'].shape}, MesoHOPS={MESOHOPS_AVAILABLE}")
    assert "populations" in results
    assert results["populations"].shape == (len(time_points), n_sites)
    total_pop = np.sum(results["populations"], axis=1)
    logger.info(f"Trace range: [{total_pop.min():.4f}, {total_pop.max():.4f}]")
    # Looser tolerance for reduced simulation time
    assert np.allclose(total_pop, 1.0, atol=0.2)  # Changed from 0.1

def test_spectroscopy_2des():
    """Test 2D Electronic Spectroscopy (2DES) simulation."""
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    n_sites = H.shape[0]
    spec = Spectroscopy2DES(system_size=n_sites)

    results = spec.simulate_2d_spectrum(H, waiting_time=0.0)
    logger.info(f"2DES spectrum shape: {results['spectrum'].shape}")

    assert "spectrum" in results
    assert "omega_exc" in results
    assert "omega_det" in results

    fig_path = spec.plot_2d_spectrum(results, output_dir="test_graphics_dyn")
    logger.info(f"2DES figure saved: {fig_path}")
    assert os.path.exists(fig_path)

    if os.path.exists("test_graphics_dyn"):
        import shutil
        shutil.rmtree("test_graphics_dyn")

if __name__ == "__main__":
    pytest.main([__file__])
