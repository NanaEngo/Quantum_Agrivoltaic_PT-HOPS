# Quantum Dynamics & Spectral Bath Engineering
> **Last updated:** 2026-05-11 | **Manuscript ID:** `jz-2026-00994t` (JPCL)

A high-performance computational framework for simulating non-Markovian quantum dynamics in photosynthetic complexes (FMO) and agrivoltaic systems. This repository implements Stochastic Bundled Dissipators (SBD) and PT-HOPS methods to investigate spectral bath engineering for enhanced energy transport.

---

## 📊 Project Status

| Component | Status | Details |
| :--- | :--- | :--- |
| **Core Simulation** | ✅ Operational | Verified on Laptop & HPC Cluster |
| **Test Coverage** | 🧪 80% (20/25) | `test_laptop_suite.py` for rapid verification |
| **Manuscript** | 📝 Major Revision | Revised LaTeX sources available in `Theory_Journals_main/JPCL/` |
| **Data Integrity** | 🔒 LFS Tracked | All HDF5/CSV results managed via Git LFS |

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
| **Laptop (Verification)** | `mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py --config Redac_Paper1/quantum_simulations_framework_parallel_260509/laptop_parameters.yaml` | 16GB RAM, 4+ Cores |
| **Production (Main)** | `mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py --parallel --skip-audit` | 128GB RAM, 24+ Cores |
| **Figure 2 Sweep (Safe)** | `mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/run_temp_sweep_only.py` | 16GB RAM (Sequential) |
| **Cluster (Generic)** | `sbatch Redac_Paper1/quantum_simulations_framework_parallel_260509/run_cluster.sh` | HPC (SLURM) |

### 2. Monitoring Progress

```bash
# Real-time log monitoring
tail -f Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/logs/execution_$(date +%Y%m%d)*.log

# Track generated results
watch -n 5 "ls -lh Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/results/"
```

---

## 📂 Repository Architecture

- **`AGENTS.md`**: Project context, hardware rules, and simulation source of truth.
- **`Redac_Paper1/`**: Primary workspace for the JPCL manuscript.
  - **`Theory_Journals_main/JPCL/`**: LaTeX sources, BibTeX, and response letters.
  - **`quantum_simulations_framework_parallel_260509/`**: Optimized simulation codebase.
    - **`core/`**: Hamiltonian factories and HOPS trajectory orchestrators.
    - **`models/`**: High-level simulators (2DES, Agrivoltaics, etc.).
    - **`reproducibility/`**: Standardized pipelines for publication figures.
- **`_bmad-output/`**: Internal planning and architecture artifacts.

---

## 📉 Simulation Parameters (Source of Truth)

All dynamics simulations read from:  
`Redac_Paper1/quantum_simulations_framework_parallel_260509/parameters.yaml`

- **Hierarchy Depth:** $L=8$ (Converged)
- **Matsubara Terms:** $K=2$
- **Time Step:** $\Delta t = 1.0$ fs
- **Bath Model:** 12-mode vibronic bath (Kleinekathöfer/Coker)

---

## ⚠️ Troubleshooting & FAQ

- **Out of Memory (OOM):** If a production run fails, check RAM usage with `free -h`. Use `run_temp_sweep_only.py` for a memory-safe sequential execution with resume capability.
- **MesoHOPS Connectivity:** Ensure `PYTHONPATH` includes the repository root if importing `mesohops` fails.
- **Test Failures:** See `TEST_FAILURES_AND_FIXES.md` for detailed explanations and laptop-optimized verification scripts.

**Slow Tests:**
Use `--timeout=60` flag to skip tests exceeding 60 seconds:
```bash
mamba run -n MesoHOP-sim pytest tests/ -v --timeout=60
```
