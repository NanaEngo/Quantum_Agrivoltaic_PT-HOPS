
import pytest
import sys
import os

# Add current dir to path
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    # Run only the high temperature decoherence test to be fast
    retcode = pytest.main([
        "tests/test_physics_validation.py::TestPhysicsValidation::test_high_temperature_decoherence",
        "-v",
        "-s"
    ])
    sys.exit(retcode)
