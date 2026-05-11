# convergence results/
> Last updated: 2026-05-11

## ⚠️ IMPORTANT — No valid convergence data exists yet

Files marked `.INVALID_FALLBACK_DATA.csv` were generated when MesoHOPS was
unavailable. The simulator fell back to a non-hierarchy solver, producing
**identical populations for L=9, L=10, and L=11** — physically impossible
and scientifically invalid.

## To generate real convergence data

Activate the MesoHOPS environment and run the audit:

```bash
mamba run -n MesoHOP-sim python reproducibility/main.py
```

or directly:

```bash
mamba run -n MesoHOP-sim python reproducibility/audit_convergence.py
```

The audit script now detects fallback mode and exits with an error if
MesoHOPS is not available, preventing invalid data from being saved.

Valid output files will be named `convergence_audit_<hash>_<timestamp>.csv`
and will show **different** population values for L=9, L=10, and L=11.
