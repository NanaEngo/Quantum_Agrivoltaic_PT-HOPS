import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add the parent directory to sys.path to allow importing from the framework
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from utils.csv_data_storage import CSVDataStorage
from utils.figure_generator import FigureGenerator
from utils.logging_config import get_logger, setup_logging


def test_csv_data_storage(tmp_path):
    """Test CSV data storage operations."""
    storage = CSVDataStorage(output_dir=str(tmp_path))

    time_fs = np.linspace(0, 100, 10)
    populations = np.random.rand(10, 7)
    coherences = np.random.rand(10)
    metrics = {"purity": np.random.rand(10)}

    csv_path = storage.save_quantum_dynamics_results(time_fs, populations, coherences, metrics)

    assert os.path.exists(csv_path)
    df = pd.read_csv(csv_path)
    assert "time_fs" in df.columns
    assert "population_site_1" in df.columns


def test_figure_generator():
    """Test figure generation and path management."""
    gen = FigureGenerator(figures_dir="test_plots")

    # Smoke test: check that it at least exists and has the directory
    assert os.path.isdir(gen.figures_dir)

    # Cleanup
    if os.path.exists("test_plots"):
        import shutil

        shutil.rmtree("test_plots")


def test_figure_generator_dpi():
    """Verify that FigureGenerator uses the mandated 600 DPI for publication figures."""
    from unittest.mock import patch
    import matplotlib.pyplot as plt
    
    gen = FigureGenerator(figures_dir="test_dpi_plots")
    
    # Mock plt.savefig to capture arguments
    with patch("matplotlib.pyplot.savefig") as mock_savefig:
        # Create dummy data
        t = np.linspace(0, 10, 5)
        pop = np.random.rand(5, 7)
        coh = np.random.rand(5)
        metrics = {"qfi": np.random.rand(5)}
        
        gen.plot_quantum_dynamics(t, pop, coh, metrics)
        
        # Check if savefig was called with dpi=600 for the PDF
        # Note: plot_quantum_dynamics saves both PDF (600 DPI) and PNG (300 DPI)
        dpi_calls = [call.kwargs.get("dpi") for call in mock_savefig.call_args_list]
        assert 600 in dpi_calls, "At least one figure must be saved with 600 DPI"
        assert 300 in dpi_calls, "PNG preview should be 300 DPI"

    # Cleanup
    if os.path.exists("test_dpi_plots"):
        import shutil
        shutil.rmtree("test_dpi_plots")


def test_logging_config():
    """Test logging initialization."""
    import logging

    # This just ensures it doesn't crash
    setup_logging(level=logging.INFO)
    logger = get_logger("test_logger")
    logger.info("Test message")
    assert logger.name == "quantum_simulations_framework.test_logger"


if __name__ == "__main__":
    pytest.main([__file__])
