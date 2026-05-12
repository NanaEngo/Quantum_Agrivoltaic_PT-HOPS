# Reproducibility Pipelines
> Last updated: 2026-05-11

This directory contains complete reproducible workflows for the Quantum Agrivoltaic PT-HOPS framework.

## Pipelines

### jpcl_resubmission/
JPCL manuscript resubmission pipeline

- **main.py** — Main reproducibility pipeline
- **config.py** — Pipeline configuration
- **stages.py** — Pipeline stages

Usage:
```bash
python -m pipelines.jpcl_resubmission.main --config config/parameters.yaml
```

### convergence_audit/
Convergence auditing pipeline

- **audit.py** — Convergence audit implementation
- **validators.py** — Audit validators

Usage:
```bash
python -m pipelines.convergence_audit.audit --config config/parameters.yaml
```

### temperature_sweep/
Temperature sweep pipeline

- **sweep.py** — Temperature sweep implementation
- **analysis.py** — Sweep analysis

Usage:
```bash
python -m pipelines.temperature_sweep.sweep --config config/parameters.yaml
```

## Configuration

All pipelines use configuration files from `config/`:
- `parameters.yaml` — Production configuration
- `laptop_parameters.yaml` — Development configuration
- `parallel_config.yaml` — Parallel execution configuration

## Notes

- All pipelines are reproducible and deterministic
- Git commit SHA is recorded in output metadata
- All random sampling uses seeded RNG
- Schema validation enforced on all outputs
