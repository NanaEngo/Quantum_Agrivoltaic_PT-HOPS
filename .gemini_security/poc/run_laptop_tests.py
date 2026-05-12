import sys
import os
import pytest
from pathlib import Path

# Define project root
project_root = "/media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel_260509"
test_file = os.path.join(project_root, "tests/test_laptop_suite.py")

# Add project root and its src to path
sys.path.insert(0, project_root)

print(f"Running laptop tests from: {test_file}")
print(f"Python path: {sys.path[:2]}")

# Run pytest
exit_code = pytest.main([
    test_file,
    "-v",
    "-s",
    "--log-cli-level=INFO"
])

sys.exit(exit_code)
