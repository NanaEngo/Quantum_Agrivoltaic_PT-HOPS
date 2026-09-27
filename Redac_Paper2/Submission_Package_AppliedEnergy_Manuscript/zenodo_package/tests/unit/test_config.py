import os

from src.config_loader import load_config


def test_load_valid_config():
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)
    assert config.quantum.fmo.sites == 8
    assert config.quantum.fmo.mode_volume_nm3 == 0.8
    assert config.simulation.temperature_k == 295.0
