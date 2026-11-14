# Selective Vibronic Excitation for Coherent Energy Transport
> **Last updated:** 2026-11-14 | Paper 1 (JPCL `jz-2026-00994t`): **Published** ✅ | Paper 2: **Renewable Energy** package ready (35/35 tests, 50 references, main 21 pp)

A high-performance computational framework for simulating non-Markovian quantum dynamics in photosynthetic complexes (FMO) and agrivoltaic systems. This repository implements Stochastic Bundled Dissipators (SBD) and PT-HOPS methods to investigate spectral bath engineering for enhanced energy transport.

---

## 📊 Project Status

| Component | Status | Details |
| :--- | :--- | :--- |
| **Core Simulation** | ✅ **Verified Stable** | 100% Trace Preservation ($L=8, K=2$) |
| **Test Coverage** | 🧪 **35 passed (Paper 2 RE package)** | `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/tests` (env `MesoHOP-sim`, verified 2026-11-14); legacy 128/1 suite frozen in `_archive/`; Paper 1 suites verified separately |
| **Paper 1 (JPCL)** | ✅ **Published** | Post-pub: decide reply to Dr T. Xiang (SBD/SI query, draft in `Redac_Paper1/docs/Xiang/`) — private reply vs erratum |
| **Paper 2 (→ Renewable Energy)** | 🎯 **RE package ready — WP1–WP6 rebuild (35/35)** | Cameroon tri-crop ST-OPV agrivoltaics: TMM optics (PM6:Y6, APT44) + 14-site LHCII quantum NESS bounds (decoupled from macro TEA) + ERA5/FvCB–Medlyn/FAO-56 microclimate + cooperative TEA/LCA/Sobol. `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/` = source of truth (main **21 pp / 50 refs** / SM 9 pp / cover + highlights 1 p.); NE→AE→SolarEnergy V2611 lineage frozen in `_archive/` |
| **Data Integrity** | 🔒 LFS Tracked | Audited production ensemble ($n=100$) |

---

## 🛠️ Environment Setup

Ensure you have the `MesoHOP-sim` conda environment activated.

```bash
# Verify environment and MesoHOPS installation
mamba run -n MesoHOP-sim python -c "import mesohops; print(f'MesoHOPS {mesohops.__version__} OK')"
```

---

## 🚀 Execution Pipelines

### 1. Command Reference

| Mode | Command | Target Hardware |
| :--- | :--- | :--- |
| **Laptop (Verification)** | `mamba run -n MesoHOP-sim python quantum_simulations_framework/reproducibility/main.py --config quantum_simulations_framework/config/laptop_parameters.yaml` | 16GB RAM, 4+ Cores |
| **Production (Main)** | `mamba run -n MesoHOP-sim python quantum_simulations_framework/reproducibility/main.py --parallel --skip-audit` | 128GB RAM, 24+ Cores |
| **Audit (Convergence)** | `mamba run -n MesoHOP-sim python quantum_simulations_framework/reproducibility/audit_convergence.py` | 128GB RAM (High Rigor) |
| **Cluster (Generic)** | `bash Redac_Paper1/run_cluster.sh` | HPC (SLURM) |

### 2. Monitoring Progress

```bash
# Real-time log monitoring
tail -f quantum_simulations_framework/reproducibility/logs/execution_$(date +%Y%m%d)*.log

# Track generated results
watch -n 5 "ls -lh quantum_simulations_framework/reproducibility/results/"
```

---

## 📂 Repository Architecture

- **`AGENTS.md`**: Project context, hardware rules, and simulation source of truth.
- **`Redac_Paper1/`**: Primary workspace for the JPCL manuscript.
  - **`Theory_Journals_main/JPCL/`**: LaTeX sources, BibTeX, and response letters.
  - **`quantum_simulations_framework/`**: **Shared simulation codebase for Papers 1 & 2**.
    - **`core/`**: Hamiltonian factories and HOPS trajectory orchestrators.
    - **`models/`**: High-level simulators (2DES, Agrivoltaics, etc.).
    - **`extensions/`**: SBD adapters and PT-HOPS noise models.
    - **`reproducibility/`**: Standardized pipelines for publication figures.
- **`Redac_Paper2/`**: Paper 2 workspace — contains only the active `Submission_Package_RenewableEnergy_Manuscript/` (LaTeX, figures, WP1–WP6 scripts/tests/data, self-contained). Retired packages & code lineage: `_archive/`.
- **`_bmad-output/`**: Internal planning and architecture artifacts.

---

## 📉 Simulation Parameters (Source of Truth)

All dynamics simulations read from:  
`quantum_simulations_framework/parameters.yaml` (Paper 1) and `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/parameters.yaml` (Paper 2, `framework_version: 2.5.0`)

- **Hierarchy Depth:** $L=8$ (Converged to MAE $\approx \num{3.10e-11}$)
- **Matsubara Terms:** $K=2$ (Physically sufficient at \qty{295}{\kelvin})
- **Time Step:** $\Delta t = 0.5$ fs
- **Bath Model:** 12-mode vibronic bath (Kleinekathöfer/Coker)

---

## ⚠️ Troubleshooting & FAQ

- **Out of Memory (OOM):** The **260512 architecture** includes a **Memory-Aware Job Scheduler**. The simulator autonomously gates worker threads based on available physical memory (caps at \qty{66.7}{\percent} RAM), preventing crashes during large ensemble runs.
- **TrajectoryError:** A common synchronization issue between noise discretization (`TAU`) and integration time step (`dt_save`) was resolved. The engine now enforces $\tau = \Delta t/2$ internally.
- **Numerical Integrity:** The framework includes an automated 23-point test suite enforcing trace preservation ($< \num{1.0e-12}$) and density matrix positivity.

**Slow Tests:**
Use `--timeout=60` flag to skip tests exceeding 60 seconds:
```bash
mamba run -n MesoHOP-sim pytest tests/ -v --timeout=60
```
