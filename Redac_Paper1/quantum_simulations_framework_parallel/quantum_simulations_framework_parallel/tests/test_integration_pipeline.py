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

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reproducibility.main import load_and_validate_config, check_environment

def test_config_loading():
    """Verify that parameters.yaml is loaded and validated correctly."""
    with patch("builtins.open", MagicMock()):
        with patch("yaml.safe_load") as mock_yaml:
            mock_yaml.return_value = {
                "dynamics": {"hierarchy_depth": 10, "matsubara_truncation": 10},
                "bath": {"temperature": 295.0}
            }
            cfg = load_and_validate_config()
            assert cfg["dynamics"]["hierarchy_depth"] == 10

def test_config_validation_failure():
    """Verify that L < 10 raises ValueError."""
    with patch("builtins.open", MagicMock()):
        with patch("yaml.safe_load") as mock_yaml:
            mock_yaml.return_value = {
                "dynamics": {"hierarchy_depth": 5, "matsubara_truncation": 10}
            }
            with pytest.raises(ValueError, match="hierarchy_depth=5 < 10"):
                load_and_validate_config()

def test_environment_check():
    """Test the environment check logic."""
    with patch("importlib.import_module") as mock_import:
        # Success case
        with patch("mesohops.__version__", "1.6"):
            assert check_environment() == True
        
        # Failure case
        mock_import.side_effect = ImportError
        with patch("builtins.print"): # Silence print
            assert check_environment() == False

@patch("reproducibility.main.run_convergence_audit")
@patch("reproducibility.main.run_full_fmo_simulation")
@patch("reproducibility.main.generate_figures")
def test_full_pipeline_flow(mock_gen_figs, mock_sim, mock_audit):
    """Verify the main execution sequence."""
    from reproducibility.main import main
    
    # Mock return values
    mock_audit.return_value = {"audit_mae_10_11": 1e-7, "csv_path": "audit.csv"}
    mock_sim.return_value = ({"filtered": {}, "broadband": {}}, np.array([0, 1]))
    
    with patch("reproducibility.main.load_and_validate_config") as mock_cfg:
        mock_cfg.return_value = {
            "dynamics": {"hierarchy_depth": 10, "matsubara_truncation": 10},
            "bath": {"temperature": 295.0}
        }
        with patch("reproducibility.main.check_environment", return_value=True):
            with patch("sys.exit") as mock_exit:
                main()
                # Ensure all steps were called
                mock_audit.assert_called_once()
                mock_sim.assert_called_once()
                mock_gen_figs.assert_called_once()
                mock_exit.assert_not_called()

def test_pipeline_exits_on_no_mesohops():
    """Ensure the pipeline exits if MesoHOPS is missing."""
    from reproducibility.main import main
    with patch("reproducibility.main.load_and_validate_config"):
        with patch("reproducibility.main.check_environment", return_value=False):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_called_with(1)

if __name__ == "__main__":
    pytest.main([__file__])
