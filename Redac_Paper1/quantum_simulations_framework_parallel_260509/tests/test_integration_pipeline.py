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
    """Test the environment check logic."""
    # Test when MesoHOPS is available
    with patch("reproducibility.main.check_environment", return_value=True):
        result = check_environment()
        logger.info(f"Environment check (MesoHOPS present): {result}")
        assert result == True

    # Test when MesoHOPS is unavailable
    with patch("reproducibility.main.check_environment", return_value=False):
        result = check_environment()
        logger.info(f"Environment check (MesoHOPS absent): {result}")
        assert result == False

@patch("reproducibility.main.run_convergence_audit")
@patch("reproducibility.main.run_full_fmo_simulation")
@patch("reproducibility.main.generate_figures")
@patch("reproducibility.main.load_and_validate_config")
@patch("reproducibility.main.check_environment")
def test_full_pipeline_flow(mock_env, mock_cfg, mock_gen_figs, mock_sim, mock_audit):
    """Verify the main execution sequence."""
    from reproducibility.main import main

    # Setup mocks
    mock_env.return_value = True
    cfg_dict = {
        "dynamics": {"L_max": DEFAULT_MAX_HIERARCHY, "matsubara_truncation": DEFAULT_N_MATSUBARA, "convergence_threshold": 1e-5},
        "bath": {"temperature": DEFAULT_TEMPERATURE}
    }
    mock_cfg.return_value = cfg_dict
    mock_audit.return_value = {"audit_maes": {8: 1e-7}, "csv_path": "audit.csv"}
    mock_sim.return_value = ({"filtered": {}, "broadband": {}}, np.array([0, 1]))

    with patch("sys.exit") as mock_exit:
        main()
        logger.info(f"Pipeline steps called — audit:{mock_audit.called}, sim:{mock_sim.called}, figs:{mock_gen_figs.called}")
        mock_audit.assert_called_once()
        mock_sim.assert_called_once()
        mock_gen_figs.assert_called_once()
        mock_exit.assert_not_called()

def test_pipeline_exits_on_no_mesohops():
    """Ensure the pipeline exits if MesoHOPS is missing."""
    with patch("reproducibility.main.check_environment", return_value=False):
        with patch("src.core.hops_simulator.MESOHOPS_AVAILABLE", False):
            with patch("reproducibility.main.load_and_validate_config"):
                with patch("sys.exit") as mock_exit:
                    from reproducibility.main import main
                    try:
                        main()
                    except SystemExit:
                        pass
                    logger.info(f"sys.exit called with: {mock_exit.call_args}")
                    mock_exit.assert_called_with(1)

if __name__ == "__main__":
    pytest.main([__file__])
