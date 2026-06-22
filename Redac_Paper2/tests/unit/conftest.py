"""Pytest fixtures for Quantum Agrivoltaics Paper 2 unit tests."""

import os

import pytest
from Redac_Paper2.src.config_loader import ConfigModel, load_config


@pytest.fixture(scope="session")
def project_root() -> str:
    """Returns the absolute path to the Redac_Paper2 project directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def config_path(project_root: str) -> str:
    """Returns the path to the canonical parameters.yaml file."""
    return os.path.join(project_root, "parameters.yaml")


@pytest.fixture(scope="session")
def config(config_path: str) -> ConfigModel:
    """Loads and returns the validated Pydantic configuration model."""
    return load_config(config_path)


@pytest.fixture
def default_solar_flux() -> float:
    """Default solar flux value for test simulations (W/m2)."""
    return 800.0


@pytest.fixture
def high_solar_flux() -> float:
    """High solar flux value exceeding the NPQ threshold (W/m2)."""
    return 1000.0
