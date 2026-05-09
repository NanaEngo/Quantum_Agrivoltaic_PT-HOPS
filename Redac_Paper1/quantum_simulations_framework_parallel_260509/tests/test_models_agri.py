import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import get_test_logger
from core.hamiltonian_factory import create_fmo_hamiltonian
from models.agrivoltaic_coupling_model import AgrivoltaicCouplingModel
from models.environmental_factors import EnvironmentalFactors
from models.spectral_optimizer import SpectralOptimizer
from core.constants import (
    DEFAULT_N_OPV_SITES,
    DEFAULT_N_PSU_SITES,
    DEFAULT_PCE,
    DEFAULT_ETR,
    SOLAR_LAMBDA_MIN,
    SOLAR_LAMBDA_MAX,
    DEFAULT_TEMPERATURE
)

logger = get_test_logger("test_models_agri")

def test_agrivoltaic_coupling_model():
    """Test spectral coupling between OPV and PSU."""
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    model = AgrivoltaicCouplingModel(fmo_hamiltonian=H)
    logger.info(f"AgrivoltaicCouplingModel: n_opv={model.n_opv_sites}, n_psu={model.n_psu_sites}, n_total={model.n_total}")
    assert model.n_opv_sites == DEFAULT_N_OPV_SITES
    assert model.n_psu_sites == H.shape[0]
    assert model.n_total == DEFAULT_N_OPV_SITES * H.shape[0]

def test_spectral_optimizer():
    """Test the spectral optimization routine."""
    lambdas = np.linspace(SOLAR_LAMBDA_MIN, SOLAR_LAMBDA_MAX, 100)
    sun = np.ones_like(lambdas)
    opv_res = np.exp(-((lambdas - 600) ** 2) / 10000)
    psu_res = np.exp(-((lambdas - 450) ** 2) / 5000) + np.exp(-((lambdas - 680) ** 2) / 5000)

    optimizer = SpectralOptimizer(
        solar_spectrum=(lambdas, sun), opv_response=opv_res, psu_response=psu_res
    )
    results = optimizer.optimize_spectral_splitting(n_filters=1, maxiter=5, popsize=4)
    logger.info(f"SpectralOptimizer: optimal_pce={results.get('optimal_pce', 'N/A'):.4f}")
    assert "optimal_pce" in results
    assert "optimal_etr" in results
    assert 0 <= results["optimal_pce"] <= 1.0

def test_environmental_factors():
    """Test environmental data generation and modeling."""
    env = EnvironmentalFactors()
    dust = env.dust_accumulation_model(np.arange(30))
    logger.info(f"Dust profile: min={dust.min():.4f}, max={dust.max():.4f}")
    assert len(dust) == 30

    # Test temperature effect
    temp_effect = env.temperature_effects_model(np.array([DEFAULT_TEMPERATURE, DEFAULT_TEMPERATURE + 10]), base_efficiency=DEFAULT_PCE)
    assert len(temp_effect) == 2

if __name__ == "__main__":
    pytest.main([__file__])
