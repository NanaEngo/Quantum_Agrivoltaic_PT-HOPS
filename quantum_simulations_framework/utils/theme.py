"""
JPCL Publication Theme — RE-EXPORT MODULE

Canonical source is src/visualization/theme.py.
This module re-exports all public symbols for backward compatibility.
"""
from src.visualization.theme import (  # noqa: F401
    apply_jpcl_theme,
    get_color_palette,
)

__all__ = ["apply_jpcl_theme", "get_color_palette"]
