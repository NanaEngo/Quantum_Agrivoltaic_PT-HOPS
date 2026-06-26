"""
Publication-quality visualization for quantum agrivoltaic simulations.

This package provides figure generation, FMO schematics, and theming.
"""

from .figure_generator import FigureGenerator
from .fmo_schematic import generate_fmo_schematic
from .theme import apply_jpcl_theme, get_color_palette

__all__ = [
    "FigureGenerator",
    "generate_fmo_schematic",
    "apply_jpcl_theme",
    "get_color_palette",
]
