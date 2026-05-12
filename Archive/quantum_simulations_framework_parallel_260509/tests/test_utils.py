import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import get_test_logger
from src.io.csv_storage import CSVDataStorage
from src.visualization.figure_generator import FigureGenerator
from utils.logging_config import get_logger, setup_logging
from src.core.hamiltonian_factory import create_fmo_hamiltonian
from src.core.constants import DEFAULT_DPI, PREVIEW_DPI

logger = get_test_logger("test_utils")

@pytest.fixture
def fmo_hamiltonian():
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    return H

def test_csv_data_storage(tmp_path, fmo_hamiltonian):
    """Test CSV data storage operations."""
    storage = CSVDataStorage(output_dir=str(tmp_path))
    n_sites = fmo_hamiltonian.shape[0]

    time_fs = np.linspace(0, 100, 10)
    populations = np.random.rand(10, n_sites)
    coherences = np.random.rand(10)
    metrics = {"purity": np.random.rand(10)}

    csv_path = storage.save_quantum_dynamics_results(time_fs, populations, coherences, metrics)
    logger.info(f"CSV saved: {csv_path}")

    assert os.path.exists(csv_path)
    df = pd.read_csv(csv_path)
    logger.info(f"CSV columns: {list(df.columns)}, rows: {len(df)}")
    assert "time_fs" in df.columns
    assert "population_site_1" in df.columns

def test_figure_generator():
    """Test figure generation and path management."""
    gen = FigureGenerator(figures_dir="test_plots")
    logger.info(f"FigureGenerator dir: {gen.figures_dir}")
    assert os.path.isdir(gen.figures_dir)

    if os.path.exists("test_plots"):
        import shutil
        shutil.rmtree("test_plots")

def test_figure_generator_dpi(fmo_hamiltonian):
    """Verify that FigureGenerator uses the mandated DPI for publication figures."""
    from unittest.mock import patch

    gen = FigureGenerator(figures_dir="test_dpi_plots")
    n_sites = fmo_hamiltonian.shape[0]

    with patch("matplotlib.pyplot.savefig") as mock_savefig:
        t = np.linspace(0, 10, 5)
        pop = np.random.rand(5, n_sites)
        coh = np.random.rand(5)
        metrics = {"qfi": np.random.rand(5)}

        gen.plot_quantum_dynamics(t, pop, coh, metrics)

        dpi_calls = [call.kwargs.get("dpi") for call in mock_savefig.call_args_list]
        logger.info(f"DPI values used in savefig calls: {dpi_calls}")
        assert DEFAULT_DPI in dpi_calls, f"At least one figure must be saved with {DEFAULT_DPI} DPI"
        assert PREVIEW_DPI in dpi_calls, f"PNG preview should be {PREVIEW_DPI} DPI"

    if os.path.exists("test_dpi_plots"):
        import shutil
        shutil.rmtree("test_dpi_plots")

def test_logging_config():
    """Test logging initialization."""
    import logging
    setup_logging(level=logging.INFO)
    _logger = get_logger("test_logger")
    _logger.info("Test message from test_logging_config")
    logger.info(f"logging_config get_logger returned: {_logger.name}")
    assert "test_logger" in _logger.name

if __name__ == "__main__":
    pytest.main([__file__])
