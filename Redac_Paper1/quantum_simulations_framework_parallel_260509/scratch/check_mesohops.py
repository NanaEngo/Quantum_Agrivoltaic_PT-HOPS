
import sys
import os

# Add the current directory to sys.path to simulate the runtime environment
sys.path.append(os.getcwd())

try:
    from core.constants import MESOHOPS_AVAILABLE
    print(f"core.constants.MESOHOPS_AVAILABLE: {MESOHOPS_AVAILABLE}")
except ImportError as e:
    print(f"Failed to import from core.constants: {e}")

try:
    import mesohops
    print(f"mesohops version: {mesohops.__version__}")
except ImportError as e:
    print(f"mesohops not available: {e}")

try:
    from models.quantum_dynamics_simulator import MESOHOPS_AVAILABLE as QDS_MESO
    print(f"models.quantum_dynamics_simulator.MESOHOPS_AVAILABLE: {QDS_MESO}")
except ImportError as e:
    print(f"Failed to import from models.quantum_dynamics_simulator: {e}")
