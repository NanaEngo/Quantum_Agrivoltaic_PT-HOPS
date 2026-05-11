# 📊 Simulation Results & Artifacts (`results/`)
> **Last updated:** 2026-05-11

This directory stores the primary outputs from the simulation pipelines. These artifacts serve as the basis for the figures and numerical claims presented in the JPCL manuscript.

---

## 🛑 Data Validity Warning

> [!CAUTION]
> **Beware of Fallback Data:** Files with the suffix `.INVALID_FALLBACK_DATA.csv` must **NEVER** be used for publication. They represent failed runs where the simulator defaulted to a simple non-hierarchy solver because the MesoHOPS environment was not correctly detected.

Valid convergence data **must** show distinct differences between hierarchy depths $L=7, 8, 9$. If traces are identical across different $L$ values, the data is invalid.

---

## 📝 Output Formats

| File Type | Pattern | Description |
| :--- | :--- | :--- |
| **Ensemble Data** | `ensemble_avg_*.csv` | Population and coherence kinetics averaged over disorder realizations. |
| **Convergence Audit** | `convergence_audit_*.csv` | Multi-hierarchy data ($L=7, 8, 9$) for verification. |
| **Temperature Sweep** | `temp_sweep_*.csv` | Efficiency metrics vs. temperature ($T = 270\text{ K} - 320\text{ K}$). |
| **Figures** | `*.pdf` / `*.png` | Publication-quality plots (600 DPI, JPCL theme). |

---

## 🛠️ Data Generation

To regenerate valid results, ensure the `MesoHOP-sim` environment is active:

```bash
# Full Production Run
mamba run -n MesoHOP-sim python reproducibility/main.py --parallel

# Targeted Convergence Audit
mamba run -n MesoHOP-sim python reproducibility/audit_convergence.py
```

---

## 🔒 Data Management

- **Git LFS:** All CSV and HDF5 files are tracked via Git Large File Storage (LFS). Ensure you have `git-lfs` installed before pushing new results.
- **Audit Logs:** Every result file is associated with an execution log in `../logs/` that contains the physics parameters and trace preservation checks.

