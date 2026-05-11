# Source Code Directory
> Last updated: 2026-05-11

This directory contains the reorganized source code for the Quantum Agrivoltaic PT-HOPS framework.

## Structure

- **core/** — Core quantum dynamics infrastructure
  - Constants, Hamiltonian factory, HOPS simulator, GPU dynamics

- **quantum/** — Quantum analysis and metrics
  - Analysis suite, spectroscopy, spectral optimization, multi-scale transformation

- **agrivoltaic/** — Agrivoltaic domain-specific models
  - Coupling model, environmental factors, LCA, biodegradability, eco-design, techno-economic

- **analysis/** — General analysis tools
  - Sensitivity analysis, convergence analysis, performance analysis

- **optimization/** — Optimization algorithms
  - Spectral optimization, parameter optimization, ensemble optimization

- **io/** — Data input/output
  - CSV storage, HDF5 storage, metadata management, validators

- **visualization/** — Visualization and plotting
  - Figure generator, FMO schematic, theme, colors, formatters

- **extensions/** — External tool integrations
  - MesoHOPS adapters, stochastic bundling, ORCA wrapper, GPU backends

## Usage

Import modules using absolute paths:

```python
from src.core.hops_simulator import HopsSimulator
from src.quantum.analysis import QuantumAnalysisSuite
from src.agrivoltaic.coupling_model import AgrivoltaicCouplingModel
```

## Notes

- All modules follow consistent naming conventions
- Clear separation of concerns
- Explicit dependency hierarchy
- Comprehensive documentation
