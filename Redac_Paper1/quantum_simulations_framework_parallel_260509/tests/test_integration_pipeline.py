"""
test_integration_pipeline.py — Integration tests for the reproducibility pipeline.
Mocks heavy simulations to test script flow and artifact generation.
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import get_test_logger
from reproducibility.main import load_and_validate_config, check_environment
from src.core.constants import DEFAULT_MAX_HIERARCHY, DEFAULT_N_MATSUBARA, DEFAULT_TEMPERATURE

logger = get_test_logger("test_integration_pipeline")


def test_config_loading():
    """Verify that parameters.yaml is loaded and validated correctly."""
    with patch("builtins.open", MagicMock()):
        with patch("yaml.safe_load") as mock_yaml:
            mock_yaml.return_value = {
                "dynamics": {"L_max": DEFAULT_MAX_HIERARCHY, "matsubara_truncation": DEFAULT_N_MATSUBARA},
                "bath": {"temperature": DEFAULT_TEMPERATURE}
            }
            cfg = load_and_validate_config()
            logger.info(f"Config loaded: L={cfg['dynamics']['L_max']}, K={cfg['dynamics']['matsubara_truncation']}")
            assert cfg["dynamics"]["L_max"] == DEFAULT_MAX_HIERARCHY

def test_config_validation_failure():
    """Verify that L < DEFAULT_MAX_HIERARCHY raises ValueError."""
    bad_L = DEFAULT_MAX_HIERARCHY - 4
    logger.info(f"Testing config rejection for L={bad_L} (min required: {DEFAULT_MAX_HIERARCHY})")
    bad_config = {
        "dynamics": {"L_max": bad_L, "matsubara_truncation": DEFAULT_N_MATSUBARA},
        "bath": {"temperature": DEFAULT_TEMPERATURE}
    }
    with patch("builtins.open", MagicMock()):
        with patch("yaml.safe_load", return_value=bad_config):
            with patch("os.path.basename", return_value="parameters.yaml"):  # Force production mode
                with pytest.raises(ValueError, match=f"hierarchy_depth={bad_L} < 8"):
                    load_and_validate_config()

def test_environment_check():
    """Test the environment check logic by controlling import of mesohops."""
    # Case 1: mesohops available
    mesohops_mock = MagicMock()
    mesohops_mock.__version__ = "1.6"
    with patch.dict(sys.modules, {"mesohops": mesohops_mock}):
        result = check_environment()
        logger.info(f"Environment check (MesoHOPS present): {result}")
        assert result is True

    # Case 2: mesohops unavailable
    # Ensure 'mesohops' isn't already cached in sys.modules
    with patch.dict(sys.modules, {}, clear=False):
        real_import = __import__

        def _import_block(name, *args, **kwargs):
            if name == "mesohops":
                raise ImportError("mesohops not installed")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=_import_block):
            result = check_environment()
            logger.info(f"Environment check (MesoHOPS absent): {result}")

@patch("reproducibility.main.run_convergence_audit")
@patch("reproducibility.main.run_full_fmo_simulation")
@patch("reproducibility.main.generate_figures")
@patch("reproducibility.main.load_and_validate_config")
@patch("reproducibility.main.check_environment")
def test_full_pipeline_flow(mock_check_environment, mock_load_cfg, mock_generate_figures, mock_run_sim, mock_run_audit):
    """Verify the main execution sequence."""
    from reproducibility.main import main

    mock_check_environment.return_value = True

    cfg_dict = {
        "dynamics": {
            "L_max": DEFAULT_MAX_HIERARCHY,
            "matsubara_truncation": DEFAULT_N_MATSUBARA,
            "convergence_threshold": 1e-5,
            # required by run_full_fmo_simulation
            "time_max": 2.0,
            "time_step": 1.0,
            "sbd_bundles_per_site": 2,
        },
        "bath": {
            "temperature": DEFAULT_TEMPERATURE,
            "reorganization_energy": 35.0,
            "drude_cutoff": 500.0,
            # keep minimal arrays to avoid simulator-side work if any function is called accidentally
            "vibronic_frequencies": [100.0],
            "huang_rhys_factors": [0.1],
            "vibronic_damping": [10.0],
        },
        "pulse": {"fwhm": 50.0, "center_freq": 12000.0},
        "spectral_filter": {
            "band_centers_nm": [750, 820],
            "bandwidth_cm": 100.0,
            "weights": [0.5, 0.5],
        },
        "simulation": {"n_traj": 1, "n_traj_temp_sweep": 1, "n_disorder_samples": 1},
    }

    mock_load_cfg.return_value = cfg_dict
    mock_run_audit.return_value = {"audit_maes": {8: 1e-7}, "csv_path": "audit.csv"}
    mock_run_sim.return_value = ({"filtered": {}, "broadband": {}}, np.array([0, 1]))
    mock_generate_figures.return_value = None

    with patch("sys.exit") as mock_exit:
        with patch.object(sys, "argv", ["main.py"]):
            main()

        logger.info(
            f"Pipeline steps called — audit:{mock_run_audit.called}, sim:{mock_run_sim.called}, figs:{mock_generate_figures.called}"
        )
        mock_run_audit.assert_called_once()
        mock_run_sim.assert_called_once()
        mock_generate_figures.assert_called_once()
        mock_exit.assert_not_called()

def test_pipeline_exits_on_no_mesohops():
    """Ensure the pipeline exits if MesoHOPS is missing."""
    cfg_dict = {
        "dynamics": {
            "L_max": DEFAULT_MAX_HIERARCHY,
            "matsubara_truncation": DEFAULT_N_MATSUBARA,
            "convergence_threshold": 1e-5,
            "time_max": 2.0,
            "time_step": 1.0,
            "sbd_bundles_per_site": 2,
        },
        "bath": {
            "temperature": DEFAULT_TEMPERATURE,
            "reorganization_energy": 35.0,
            "drude_cutoff": 500.0,
            "vibronic_frequencies": [100.0],
            "huang_rhys_factors": [0.1],
            "vibronic_damping": [10.0],
        },
        "simulation": {"n_traj": 1, "n_traj_temp_sweep": 1, "n_disorder_samples": 1},
    }

    with patch("reproducibility.main.check_environment", return_value=False):
        with patch("reproducibility.main.load_and_validate_config", return_value=cfg_dict):
            with patch("sys.exit") as mock_exit:
                from reproducibility.main import main
                with patch.object(sys, "argv", ["main.py"]):
                    try:
                        main()
                    except SystemExit:
                        pass
                logger.info(f"sys.exit called with: {mock_exit.call_args}")
                mock_exit.assert_called_with(1)

if __name__ == "__main__":
    pytest.main([__file__])
