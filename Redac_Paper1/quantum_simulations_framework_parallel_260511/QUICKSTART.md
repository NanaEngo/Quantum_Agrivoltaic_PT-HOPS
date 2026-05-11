# Quick Start Guide — Quantum Agrivoltaic PT-HOPS (Parallel/GPU)

## 🛠 Installation

```bash
# 1. Activate MesoHOP-sim environment
mamba activate MesoHOP-sim

# 2. Install GPU dependencies (optional but recommended)
pip install cupy-cuda12x "jax[cuda12]"

# 3. Verify hardware visibility
mamba run -n MesoHOP-sim python -c "import jax; print(f'JAX Devices: {jax.devices()}')"
```

---

## 🚀 "Good Commands" for Production

### 1. The Production Suite
Run the full JPCL production ensemble ($L=8, K=2, N=100$) including all figures:

```bash
mamba run -n MesoHOP-sim python reproducibility/main.py --parallel --skip-audit
```

### 2. Environmental Robustness (Figure 2)
Run the temperature sweep and disorder sampling for Figure 2. This includes **Resume Logic** to handle interruptions:

```bash
# Laptop/Sequential (Safe)
mamba run -n MesoHOP-sim python reproducibility/run_temp_sweep_only.py

# Server/Parallel (High Performance)
chmod +x reproducibility/run_temp_sweep_cluster.sh
./reproducibility/run_temp_sweep_cluster.sh
```

### 3. The Verification Suite
Run the 12-test validation suite required for the Supporting Information:

```bash
mamba run -n MesoHOP-sim pytest tests/ -v
```

### 3. Monitoring & Housekeeping
```bash
# Live log monitoring
tail -f reproducibility/logs/execution_*.log

# Check result file generation
watch -n 5 "ls -lh reproducibility/results/"

# Cleanup temporary files
rm reproducibility/logs/*.log
```

---

## ⚙️ Configuration (parameters.yaml)

This file is the **Single Source of Truth**. All physics parameters are centralized here:
- **`L_max`**: 8 (Hierarchy depth)
- **`matsubara_truncation`**: 2 (Matsubara terms)
- **`time_step`**: 1.0 (fs)
- **`n_traj`**: 100 (Ensemble size)

---

## ⚠️ Troubleshooting

**Out of Memory (RAM):**
If parallel workers crash, reduce `n_workers` in `parallel_config.yaml`. 
- For the Figure 2 sweep, use `run_temp_sweep_only.py`. It defaults to sequential mode and includes **Resume Logic** to pick up from the last completed trajectory after a crash.

**MesoHOPS Not Found:**
Ensure you are using the `mamba run -n MesoHOP-sim` wrapper. This ensures all C-extensions and environment variables are correctly loaded.

---

**Last Updated:** May 10, 2026
**Project Status:** JPCL Major Revision (Production Stabilized)
