# 📊 Simulation Results & Artifacts (`results/`)
> **Last updated:** 2026-05-13

This directory stores the primary outputs from the simulation pipelines. These artifacts serve as the basis for the figures and numerical claims presented in the JPCL manuscript.

---

## 🛑 Data Validity Warning

> [!CAUTION]
> **Beware of Fallback Data:** Files with the suffix `.INVALID_FALLBACK_DATA.csv` must **NEVER** be used for publication. They represent failed runs where the simulator defaulted to a simple non-hierarchy solver because the MesoHOPS environment was not correctly detected.

Valid convergence data **must** show distinct differences between hierarchy depths $L=7, 8$. If traces are identical across different $L$ values, the data is invalid. The current production results are verified at $L=8$ with a residual MAE of \num{3.10e-11}.

---

## 📝 Output Formats

| File Type | Pattern | Description |
| :--- | :--- | :--- |
| **Ensemble Data** | `ensemble_avg_*.csv` | $n=100$ kinetics averaged over disorder realizations. |
| **Convergence Audit** | `convergence_audit_*.csv` | Multi-hierarchy data ($L=7, 8, 9$) for verification. |
| **Temperature Sweep** | `temp_sweep_*.csv` | Efficiency metrics vs. temperature ($T = \qtyrange{275}{315}{\kelvin}$). |
| **Figures** | `*.pdf` / `*.png` | **600 DPI** plots using the centralized JPCL theme. |

---

## 🛠️ Data Generation

To regenerate valid results, ensure the `MesoHOP-sim` environment is active:

```bash
# Full Production Run (Ensemble n=100)
mamba run -n MesoHOP-sim python reproducibility/main.py --parallel

# Targeted Convergence Audit (L=8 vs L=9)
mamba run -n MesoHOP-sim python reproducibility/audit_convergence.py
```

---

## 🔒 Data Management

- **Git LFS:** All CSV and HDF5 files are tracked via Git Large File Storage (LFS).
- **Audit Logs:** Every result file is associated with an execution log in `../logs/` that contains the physics parameters and trace preservation checks ($< \num{1.0e-12}$).
- **Visualization:** Figures in this directory are generated using the `FigureGenerator` utility, enforcing JPCL legibility standards (Arial fonts, 600 DPI, \unit{\femto\second} units).

