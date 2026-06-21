"""
Stochastically Bundled Dissipators — RE-EXPORT MODULE

Canonical source is src/extensions/stochastic_bundling.py.
This module re-exports all public symbols for backward compatibility.
"""
from src.extensions.stochastic_bundling import (  # noqa: F401
    StochasticBundle,
    StochasticallyBundledDissipator,
)

__all__ = ["StochasticBundle", "StochasticallyBundledDissipator"]
