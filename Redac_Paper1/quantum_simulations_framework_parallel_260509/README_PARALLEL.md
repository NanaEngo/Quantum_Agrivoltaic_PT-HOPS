# Quantum Agrivoltaic PT-HOPS — Parallel/GPU Version

This is the high-performance parallelized version of the quantum agrivoltaic simulation framework, optimized for JPCL production-grade ensembles.

## 🚀 "Good Commands" Cheat Sheet

### 🖥️ Local High-Memory Run (128GB+ RAM)
```bash
mamba run -n MesoHOP-sim python reproducibility/main.py --parallel --skip-audit
```

### 💻 Laptop Verification (16GB RAM)
```bash
mamba run -n MesoHOP-sim python reproducibility/main.py --config laptop_parameters.yaml
```

### 🔬 Convergence Audit (Step-by-step)
```bash
# Run only the audit without the full ensemble
mamba run -n MesoHOP-sim python reproducibility/audit_convergence.py
```

### 📊 Monitoring progress
```bash
# View last 50 lines of log every 2 seconds
watch -n 2 "tail -n 50 reproducibility/logs/execution_*.log"
```

---

## 🛠 Hardware Configuration

The system uses `joblib` for CPU parallelization and `JAX/CuPy` for optional GPU acceleration. 

Edit `parallel_config.yaml` to tune performance:
- `n_workers`: Number of parallel trajectory workers.
- `use_gpu`: Enable JAX-accelerated matrix operations.
- `trajectory_batch_size`: Number of trajectories per GPU batch.

---

## 📂 Architecture (May 10 Stable)

- **`reproducibility/main.py`**: Unified entry point for audits and production runs.
- **`core/hops_simulator.py`**: Parallel-hardened trajectory engine.
- **`utils/figure_generator.py`**: JPCL-themed plotting (600 DPI, Time [fs]).
- **`parameters.yaml`**: The single source of truth for all physics parameters.

---

## 📑 Reproducibility & Stability

- **Hierarchy Depth ($L$):** Stabilized at $L=8$ for the FMO production ensemble.
- **Matsubara Terms ($K$):** Truncated at $K=2$ (MAE < $1 \times 10^{-4}$ vs $K=3$).
- **Time Grid:** Fixed at $1.0$ fs step for 12-mode vibronic stability.
- **Randomness:** All disorder sampling uses a seeded RNG (`seed=42`).

---

**Corresponding Author**: Steve Cabrel Teguia Kouam  
**Last Updated**: May 10, 2026
