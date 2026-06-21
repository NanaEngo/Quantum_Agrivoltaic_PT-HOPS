"""
Quantum dynamics and analysis modules.

This package provides quantum analysis tools, multi-scale transformers,
spectral optimization, and spectroscopy simulations.
"""

from .analysis import QuantumAnalysisSuite
from .multi_scale import MultiScaleTransformer
from .spectral_optimization import SpectralOptimizer
from .spectroscopy import Spectroscopy2DES

__all__ = [
    "QuantumAnalysisSuite",
    "MultiScaleTransformer",
    "SpectralOptimizer",
    "Spectroscopy2DES",
]
