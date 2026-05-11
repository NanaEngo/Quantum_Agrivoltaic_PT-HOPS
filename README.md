# Quantum Dynamics & Spectral Bath Engineering

Computational framework, simulation pipelines, and manuscript source files for non-Markovian quantum dynamics in photosynthesis and agrivoltaics. This repository is currently optimized for the **JPCL Major Revision** of the manuscript *Spectral Bath Engineering via Non-Markovian Dynamics in the FMO Complex* (jz-2026-00994t).

**Status:** ✅ All 9 core components verified operational | 🧪 20/25 tests passing (80%) | 📊 Laptop-friendly test suite available

---

## 🛠️ Environment Setup

All simulations require the `MesoHOP-sim` conda environment.

```bash
# Verify environment health
mamba env list | grep MesoHOP-sim
mamba run -n MesoHOP-sim python -c "import mesohops; print(f'MesoHOPS {mesohops.__version__} OK')"
```

---

## 🚀 Command Reference

### 1. Execution Pipelines

| Mode | Command | Target Hardware |
| :--- | :--- | :--- |
| **Laptop (Verification)** | `mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py --config Redac_Paper1/quantum_simulations_framework_parallel_260509/laptop_parameters.yaml` | 16GB RAM, 4+ Cores |
| **Production (Main)** | `mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py --parallel --skip-audit` | 128GB RAM, 24+ Cores |
| **Figure 2 Sweep (Safe)** | `mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/run_temp_sweep_only.py` | 16GB RAM (Sequential) |
| **Figure 2 Sweep (Server)**| `./Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/run_temp_sweep_cluster.sh` | Cluster (Parallel + Resume) |
| **Cluster (Generic)** | `sbatch Redac_Paper1/quantum_simulations_framework_parallel_260509/run_cluster.sh` | HPC (SLURM) |

### 2. Monitoring & Live Logs

Monitor the production ensemble progress in real-time:

```bash
# Follow the latest execution log
tail -f Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/logs/execution_$(date +%Y%m%d)*.log

# Watch result file generation
watch -n 5 "ls -lh Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/results/"
```

### 3. Verification & Audits

Run the test suite with appropriate scope for your hardware:

```bash
# Laptop Quick Verification (30 seconds)
mamba run -n MesoHOP-sim pytest Redac_Paper1/quantum_simulations_framework_parallel_260509/tests/test_laptop_suite.py -v

# Full SI Validation Suite (15+ minutes)
mamba run -n MesoHOP-sim pytest Redac_Paper1/quantum_simulations_framework_parallel_260509/tests/ -v --timeout=60

# Skip slow integration tests
mamba run -n MesoHOP-sim pytest Redac_Paper1/quantum_simulations_framework_parallel_260509/tests/ -v -k "not test_full_pipeline_flow"

# Manually verify trace preservation in results
grep "Trace OK" Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/logs/*.log
```

### 4. Housekeeping & Cleanup

Keep the workspace clean and manage large data files:

```bash
# Clean up temporary logs
rm Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/logs/*.log

# Check disk usage of simulation data
du -sh Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/results/

# Verify Git LFS tracking for HDF5/CSV
git lfs status
```

### 5. Manuscript Compilation (JPCL Letter)

```bash
cd Redac_Paper1/Theory_Journals_main/JPCL/
latexmk -pdf Manuscript_JPCL_26-05-10.tex SI_JPCL_26-05-10.tex
```

---

## 📉 Parameter Source of Truth

All simulations read from a single centralized configuration. Do not hardcode physics values.

*   **Canonical Config:** `Redac_Paper1/quantum_simulations_framework_parallel_260509/parameters.yaml`
*   **Production Truncation:** $L=8$, $K=2$
*   **Time Step:** $\Delta t = 1.0$ fs (Optimized for 12-mode bath stability)

---

## 📂 Repository Structure

```text
.
├── AGENTS.md                          # Project status and agent rules
├── Redac_Paper1/
│   ├── Theory_Journals_main/JPCL/     # Manuscript & SI (Target: JPCL)
│   └── quantum_simulations_framework_parallel_260509/ # Core Codebase
│       ├── parameters.yaml            # GLOBAL SOURCE OF TRUTH
│       ├── reproducibility/           # main.py and result analysis
│       ├── core/                      # HopsSimulator & Hamiltonian
│       └── tests/                     # 12-test validation suite
└── _bmad-output/                      # Planning artifacts
```

---

## ⚠️ Troubleshooting

**Out of Memory (OOM):**
If a production run crashes, check available RAM: `free -h`. 
- **Main Pipeline:** Reduce `n_workers` in `parallel_config.yaml`.
- **Figure 2 Sweep:** Use the standalone `run_temp_sweep_only.py`. It defaults to sequential execution (1 worker) and includes **Resume Logic** to pick up from where the crash occurred.

**MesoHOPS Fallback:**
If you see "MesoHOPS NOT found", ensure your `PYTHONPATH` includes the framework directory or use the `mamba run` wrapper as shown above.

**Test Failures on Laptop:**
See [TEST_FAILURES_AND_FIXES.md](TEST_FAILURES_AND_FIXES.md) for:
- Root causes of 5 failing tests (80% pass rate)
- Laptop-friendly test suite (`test_laptop_suite.py`) for 30-second verification
- Fixes for integration tests with reduced simulation time

**Slow Tests:**
Use `--timeout=60` flag to skip tests exceeding 60 seconds:
```bash
mamba run -n MesoHOP-sim pytest tests/ -v --timeout=60
```
