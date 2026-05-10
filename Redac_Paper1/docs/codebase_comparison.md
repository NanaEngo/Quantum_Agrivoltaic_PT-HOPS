# Codebase Status: Canonical JPCL Framework

**Canonical Reference (Local):** `Redac_Paper1/quantum_simulations_framework_parallel_260509/`
*(Note: Server-side deployment stubs have been merged and deprecated; local is now the single source of truth).*
**Date:** 2026-05-10

---

## 1. Directory Structure & Audit Status

| Path | Status | Details |
|------|--------|---------|
| `parameters.yaml` | ✅ Validated | Stabilized at L=8, K=2 |
| `core/constants.py` | ✅ Validated | Synchronized with parameters.yaml |
| `core/hops_simulator.py` | ✅ Audited | Full NumPy docstrings added |
| `core/hamiltonian_factory.py` | ✅ Reconciled | Merged server best practices (Type hints, np.diag) |
| `core/gpu_dynamics.py` | ✅ Functional | CuPy native CUDA with JAX fallback |
| `models/quantum_dynamics_simulator.py` | ✅ Audited | Detailed docstrings for parallel workers |
| `models/simple_quantum_dynamics_simulator.py` | ✅ Audited | Unitary evolution fallback engine |
| `reproducibility/main.py` | ✅ Stabilized | Production suite (--parallel --skip-audit) |
| `utils/csv_data_storage.py` | ✅ Reconciled | Using rich local storage with SHA-256 integrity |
| `utils/figure_generator.py` | ✅ Reconciled | JPCL-themed (600 DPI, Time [fs]) |
| `tests/test_jpcl_resubmission_suite.py` | ✅ Passing | 12-test SI validation suite |

---

## 2. Final Reconciliation Summary

As of 2026-05-10, all server-side best practices have been successfully merged into the canonical local codebase. The standalone server directory has been deprecated and removed.

### Improvements Merged:
- **Hamiltonian Factory**: Adopted the server's Python 3.10+ type hints and NumPy-style docstrings. Improved numerical stability by using `np.diag` for diagonal energy shifts.
- **Documentation**: Completed a full audit of `core/` and `models/` docstrings to meet publication standards.
- **Data Integrity**: Verified that the local `csv_data_storage.py` (which uses SHA-256 hashing and YAML audit trails) is the production standard for results storage.

### Data Format Confirmation:
The production ensemble CSVs (`fmo_dynamics_ensemble_*.csv`) follow the **Local Format**:
- **Populations**: Per-site columns.
- **Coherences**: Single aggregated scalar column (L1-norm).
- **Metadata**: Embedded SHA-256 hash in filename for provenance tracking.

---

## 3. Deployment Strategy

Future server deployments should be performed by cloning the canonical `Redac_Paper1/quantum_simulations_framework_parallel_260509/` directory directly. The previous "stripped-down" deployment strategy is deprecated in favor of environment-identical execution.

**Last Updated:** May 10, 2026  
**Status:** **RECONCILIATION COMPLETE**
