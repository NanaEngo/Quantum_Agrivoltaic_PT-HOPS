"""
Import Path Standardizer

Enforces consistent absolute imports across the codebase to prevent
dual import paths (from core.X vs from ..core.X) that can cause
module reloading and state inconsistencies.

Usage:
------
At the top of any module in the framework:

    from utils.import_standardizer import ensure_framework_imports
    ensure_framework_imports()

This ensures that all subsequent imports use absolute paths relative
to the framework root, preventing import duplication.
"""

import os
import sys
from pathlib import Path


def get_framework_root() -> Path:
    """
    Locate the framework root directory.
    
    Returns the parent of the directory containing this file
    (i.e., the quantum_simulations_framework_parallel_260509 directory).
    
    Returns
    -------
    Path
        Absolute path to framework root
    """
    return Path(__file__).parent.parent.absolute()


def ensure_framework_imports() -> None:
    """
    Ensure framework root is in sys.path for absolute imports.
    
    Call this at module import time to guarantee that all subsequent
    imports use absolute paths (from core.X, from models.Y, etc.)
    rather than relative paths (from ..core.X).
    
    This prevents module duplication and state inconsistencies that
    can occur when the same module is imported via multiple paths.
    """
    framework_root = get_framework_root()
    
    if str(framework_root) not in sys.path:
        sys.path.insert(0, str(framework_root))


def validate_import_consistency() -> dict:
    """
    Validate that no modules are imported via multiple paths.
    
    Returns
    -------
    dict
        Dictionary with keys:
        - 'duplicates': list of module names imported via multiple paths
        - 'status': 'OK' if no duplicates, 'WARNING' if duplicates found
        - 'details': dict mapping module names to their import paths
    """
    module_paths = {}
    duplicates = []
    
    for module_name, module in sys.modules.items():
        if module is None or not hasattr(module, '__file__'):
            continue
        
        # Skip standard library and third-party packages
        if 'site-packages' in str(module.__file__):
            continue
        
        # Track framework modules
        if 'quantum_simulations_framework' in str(module.__file__):
            if module_name in module_paths:
                if module_paths[module_name] != module.__file__:
                    duplicates.append(module_name)
            else:
                module_paths[module_name] = module.__file__
    
    return {
        'duplicates': duplicates,
        'status': 'OK' if not duplicates else 'WARNING',
        'details': module_paths,
    }


# Recommended import patterns (use these, not relative imports):
"""
CORRECT (Absolute Imports):
    from src.core.hops_simulator import HopsSimulator
    from src.quantum.analysis import QuantumDynamicsSimulator
    from src.io.csv_storage import CSVDataStorage
    from src.extensions.mesohops_adapters import MesoHOPSAdapter

INCORRECT (Relative Imports - avoid):
    from ..core.hops_simulator import HopsSimulator
    from ...models.quantum_dynamics_simulator import QuantumDynamicsSimulator
    from ..utils.csv_data_storage import CSVDataStorage
"""
