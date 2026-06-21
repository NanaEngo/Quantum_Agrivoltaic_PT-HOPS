"""
Models module for quantum agrivoltaic simulations.

⚠️ RE-EXPORT MODULE — Canonical sources are in src/agrivoltaic/, src/quantum/,
   src/analysis/. This module re-exports all public symbols for backward
   compatibility.
"""

from src.agrivoltaic.coupling_model import AgrivoltaicCouplingModel
from src.agrivoltaic.biodegradability_analyzer import BiodegradabilityAnalyzer
from src.agrivoltaic.eco_design_analyzer import EcoDesignAnalyzer
from src.agrivoltaic.environmental_factors import EnvironmentalFactors
from src.agrivoltaic.lca_analyzer import LCAAnalyzer
from src.agrivoltaic.techno_economic_model import TechnoEconomicModel
from src.analysis.sensitivity_analyzer import SensitivityAnalyzer
from src.quantum.multi_scale import MultiScaleTransformer
from src.quantum.spectral_optimization import SpectralOptimizer
from src.quantum.spectroscopy import Spectroscopy2DES

# Re-exported from src/quantum/ for backward compatibility
from src.quantum.quantum_dynamics_simulator import QuantumDynamicsSimulator
from src.quantum.simple_quantum_dynamics_simulator import SimpleQuantumDynamicsSimulator

__all__ = [
    "AgrivoltaicCouplingModel",
    "BiodegradabilityAnalyzer",
    "EcoDesignAnalyzer",
    "EnvironmentalFactors",
    "LCAAnalyzer",
    "MultiScaleTransformer",
    "QuantumDynamicsSimulator",
    "SensitivityAnalyzer",
    "SimpleQuantumDynamicsSimulator",
    "SpectralOptimizer",
    "Spectroscopy2DES",
    "TechnoEconomicModel",
]
