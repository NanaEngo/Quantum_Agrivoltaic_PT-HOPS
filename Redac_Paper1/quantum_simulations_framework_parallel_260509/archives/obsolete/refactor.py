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

qds_content = re.sub(r"try:\n\s*from core\.constants import \([^)]+\)\nexcept ImportError:\n\s*", 
                     r"from core.constants import (\n        DEFAULT_MAX_HIERARCHY, DEFAULT_N_MATSUBARA, DEFAULT_TEMPERATURE,\n        DEFAULT_REORGANIZATION_ENERGY, DEFAULT_DRUDE_CUTOFF,\n        DEFAULT_N_TRAJ, DEFAULT_MAX_TIME, MEMORY_FRACTION_LIMIT, \n        BASE_TRAJ_MEMORY_GB, MIN_TRAJ_MEMORY_GB,\n    )\n", 
                     qds_content, flags=re.DOTALL)

# Add import for QuantumAnalysisSuite
if "from models.quantum_analysis import QuantumAnalysisSuite" not in qds_content:
    import_idx = qds_content.find("import logging")
    qds_content = qds_content[:import_idx] + "from models.quantum_analysis import QuantumAnalysisSuite\n" + qds_content[import_idx:]

# 2. Extract methods
start_idx = qds_content.find("    def calculate_etr(self, populations, time_points):")
end_idx = qds_content.find("def spectral_density_drude_lorentz")

if start_idx != -1 and end_idx != -1:
    qds_content = qds_content[:start_idx] + qds_content[end_idx:]

# 3. Instantiate analyzer and replace usages
init_idx = qds_content.find("        self.lambda_reorg = lambda_reorg")
if "self.analyzer = QuantumAnalysisSuite()" not in qds_content and init_idx != -1:
    qds_content = qds_content[:init_idx] + "        self.analyzer = QuantumAnalysisSuite()\n" + qds_content[init_idx:]

# 4. Replace `self.calculate_` with `self.analyzer.calculate_` in simulate_dynamics
qds_content = re.sub(r"self\.calculate_", "self.analyzer.calculate_", qds_content)

with open(qds_path, 'w') as f:
    f.write(qds_content)
print("quantum_dynamics_simulator.py refactored successfully.")
