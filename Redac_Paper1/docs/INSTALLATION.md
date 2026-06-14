# Installation & Environment Setup
> **Target Environment:** `MesoHOP-sim` (Conda/Mamba)

This framework requires a specialized Python 3.10 environment with `mesohops` and `joblib` parallelization support.

## 1. Environment Creation

It is recommended to use `mamba` for faster dependency resolution.

```bash
# Create and activate the core environment
mamba create -n MesoHOP-sim python=3.10 -y
mamba activate MesoHOP-sim
```

## 2. Dependency Installation

Install the required numerical stack and the MesoHOPS solver:

```bash
# Install core dependencies (NumPy, SciPy, Joblib, etc.)
mamba run -n MesoHOP-sim pip install -r Redac_Paper1/docs/requirements.txt

# Install MesoHOPS specific components
mamba run -n MesoHOP-sim pip install -r Redac_Paper1/docs/requirements-mesohops.txt
```

## 3. Verification

Verify that the environment is correctly configured by running the minimal test suite:

```bash
# Run 5-point verification suite
mamba run -n MesoHOP-sim pytest Redac_Paper1/quantum_simulations_framework_parallel_260512/tests/ -v -k "minimal"
```

## Technical Notes
- **MesoHOPS Version:** This framework is validated against MesoHOPS v1.6+.
- **Parallelization:** Ensure `joblib` is installed to utilize the multi-core `TrajectoryManager`.
- **Memory Requirements:** Production runs ($L=8$) require \qty{128}{GB} RAM nodes.
