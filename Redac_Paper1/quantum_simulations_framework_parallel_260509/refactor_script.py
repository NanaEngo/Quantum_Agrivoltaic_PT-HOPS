import os
import re

base_dir = "/media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel_260509"
qds_path = os.path.join(base_dir, "models/quantum_dynamics_simulator.py")

with open(qds_path, 'r') as f:
    qds_content = f.read()

# 1. Standardize imports in the codebase
for root, dirs, files in os.walk(os.path.join(base_dir, "models")):
    for file in files:
        if file.endswith(".py"):
            fpath = os.path.join(root, file)
            with open(fpath, 'r') as f:
                content = f.read()
            # Replace 'from ..core' with 'from core'
            new_content = re.sub(r'from \.\.core', 'from core', content)
            if new_content != content:
                with open(fpath, 'w') as f:
                    f.write(new_content)
                print(f"Standardized imports in {file}")

# Fix the specific try-except fallback in quantum_dynamics_simulator.py
fallback_pattern = r"except ImportError:\s*# Relative fallback.*?\n\s*from \.\.core\.constants import \([^)]+\)"
qds_content = re.sub(fallback_pattern, "", qds_content, flags=re.DOTALL)

# Remove the try/except entirely if it leaves an empty except
qds_content = re.sub(r"try:\n\s*from core\.constants import \([^)]+\)\nexcept ImportError:\n\s*", 
                     r"from core.constants import (\n        DEFAULT_MAX_HIERARCHY, DEFAULT_N_MATSUBARA, DEFAULT_TEMPERATURE,\n        DEFAULT_REORGANIZATION_ENERGY, DEFAULT_DRUDE_CUTOFF,\n        DEFAULT_N_TRAJ, DEFAULT_MAX_TIME, MEMORY_FRACTION_LIMIT, \n        BASE_TRAJ_MEMORY_GB, MIN_TRAJ_MEMORY_GB,\n    )\n", 
                     qds_content, flags=re.DOTALL)


# 2. Extract methods
# We will find the start of calculate_etr and the end of stochastically_bundled_dissipators
start_idx = qds_content.find("    def calculate_etr(self, populations, time_points):")
end_idx = qds_content.find("    def spectral_density_drude_lorentz")

if start_idx == -1 or end_idx == -1:
    print("Could not find the bounds for extraction.")
    exit(1)

# Ensure we go up to the end of the method before spectral_density
extracted_content = qds_content[start_idx:end_idx].rstrip() + "\n"

# Remove extracted content from original
new_qds_content = qds_content[:start_idx] + qds_content[end_idx:]

# 3. Create models/quantum_analysis.py
qa_content = '''import numpy as np
import scipy.linalg as la
import logging
from typing import List, Tuple, Dict, Optional, Union, Any
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

class QuantumAnalysisSuite:
    """
    Suite of analysis methods for quantum dynamics simulations.
    Provides methods to calculate coherence, entanglement, ETR, and other quantum metrics.
    """
'''

# We need to process the extracted methods to:
# a) keep `self` but maybe add types
# Wait, `self` in analyze_robustness refers to QuantumDynamicsSimulator.
# So QuantumAnalysisSuite needs a reference to the simulator or we just make these static methods.
# For `analyze_robustness`, it uses self.H_raw, self.lambda_reorg, self.gamma_dl, self.k_matsubara, self.max_hier, self.n_traj, self.temperature, self.n_sites.
# It also initializes `QuantumDynamicsSimulator`. It's better to keep `analyze_robustness` in `QuantumDynamicsSimulator`.

with open("extract_test.txt", "w") as f:
    f.write("Extracted successfully")
