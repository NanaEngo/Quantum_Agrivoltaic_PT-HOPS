# 💎 Converged Production Data (`data/converged/`)
> **Last updated:** 2026-05-11

This directory is the canonical storage location for high-rigor, converged simulation outputs used for the final figures in the JPCL manuscript.

---

## 📐 Canonical Parameters
All data stored here must strictly adhere to the finalized production configuration:
- **Hierarchy Depth:** $L=8$
- **Matsubara Terms:** $K=2$
- **Sampling:** 100 disorder realizations
- **Method:** PT-HOPS with Stochastic Bundled Dissipators (SBD)

---

## 🔒 Storage & Versioning

- **Format:** Data is primarily stored as HDF5 (`.h5`) files to preserve full trajectory metadata and high numerical precision.
- **Git LFS:** **MANDATORY.** Never commit `.h5` or large `.csv` files without Git Large File Storage (LFS) configured.
- **Verification:** Only files that have passed the `audit_convergence.py` trace and positivity checks should be moved to this directory.

---

## 🚀 Generation Command

To generate and verify production-grade data:
```bash
mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py --parallel --skip-audit
```

