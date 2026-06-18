# Quick Start Guide: Quantum-Enhanced Agrivoltaics PT-HOPS

This document provides essential instructions for setting up the environment and 
executing the production-grade simulations for the JPCL manuscript 
*"Quantum-Enhanced Agrivoltaics via Spectral Bath Engineering"* (jz-2026-00994t).

---

## 🛠 Installation & Setup

The framework requires the `MesoHOP-sim` environment, which bundles the 
`MesoHOPS v1.6` solver with high-performance numerical backends.

```bash
# 1. Activate the optimized environment
mamba activate MesoHOP-sim

# 2. Install hardware-specific dependencies (CUDA 12.x)
pip install cupy-cuda12x "jax[cuda12]"

# 3. Verify hardware visibility (GPU support)
mamba run -n MesoHOP-sim python -c "import jax; print(f'JAX Devices: {jax.devices()}')"
```

---

## 🚀 Canonical Production Commands

### 1. Main Ensemble Dynamics (Figure 1)
To replicate the full FMO ensemble transport dynamics ($L=8, K=2, N=100$ realizations):

```bash
mamba run -n MesoHOP-sim python reproducibility/main.py --parallel --skip-audit
```

### 2. Environmental Robustness (Figure 2)
The temperature and disorder sensitivity sweep involves high-computational 
cost. The script includes **Resume Capability** to handle interruptions 
automatically.

```bash
# Production Execution (Cluster/HPC)
chmod +x reproducibility/run_temp_sweep_cluster.sh
./reproducibility/run_temp_sweep_cluster.sh

# Fast Verification (Laptop Mode)
mamba run -n MesoHOP-sim python reproducibility/run_temp_sweep_only.py
```

### 3. Numerical Verification (Supporting Information)
Execute the 12-point validation suite to verify physical consistency:

```bash
mamba run -n MesoHOP-sim pytest tests/ -v
```

---

## ⚙️ Configuration Source of Truth

The framework follows a **Strict Parameter Mandate**. All physical constants 
and simulation parameters are controlled via `parameters.yaml`.

| Parameter | Production Value | Description |
|-----------|------------------|-------------|
| `L_max` | 8 | Hierarchy truncation depth |
| `K` | 2 | Matsubara expansion terms |
| `dt` | 1.0 fs | Propagation time step |
| `n_traj` | 100 | Ensemble size for FMO dynamics |

---

## ⚠️ Known Issues & Troubleshooting

- **Out of Memory (OOM):** If parallel workers crash on high-L runs, reduce 
  `n_workers` in `parallel_config.yaml` or use the sequential execution 
  script `run_temp_sweep_only.py`.
- **Trace Loss:** A warning regarding "Stochastic Norm Loss" in single 
  trajectories is expected behavior in HOPS; however, the ensemble average 
  must preserve the trace within $\pm 10^{-4}$.

---
**Last Updated:** 2026-05-11  
**Status:** Production (Revision jz-2026-00994t)
