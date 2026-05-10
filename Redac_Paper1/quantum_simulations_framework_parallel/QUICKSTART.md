# Quick Start Guide — Parallel/GPU Version

## Installation (One-time setup)

```bash
# 1. Activate environment
mamba activate MesoHOP-sim

# 2. Install CuPy with CUDA support (RECOMMENDED - native CUDA)
pip install cupy-cuda12x

# 3. Alternative: Install JAX with CUDA (fallback)
pip install --upgrade "jax[cuda12]"

# 4. Verify GPU availability
python -c "
import cupy as cp
print(f'CuPy: {cp.__version__}')
print(f'CUDA: {cp.cuda.runtime.runtimeGetVersion()}')
print(f'Device: {cp.cuda.Device(0).name.decode()}')
"
# Expected: CuPy version, CUDA version, GPU name (RTX A4000)
```

**Note:** CuPy is preferred (native CUDA), JAX is fallback. The code automatically selects the best available backend.

## Usage

### Run Benchmark (Recommended first step)
```bash
cd /home/tchapet/Documents/GitHub/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel

mamba run -n MesoHOP-sim python benchmark_parallel.py
```

This will test:
- Single-threaded CPU performance
- 40-worker parallel CPU performance
- GPU batch performance (if JAX available)

### Run Parallel Simulation
```bash
cd /home/tchapet/Documents/GitHub/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel

mamba run -n MesoHOP-sim python -u reproducibility/main_parallel.py
```

## Configuration

Edit `parallel_config.yaml` to adjust settings:

### For CPU-heavy workloads
```yaml
parallel:
  n_workers: 46          # Use more cores
  use_gpu: false         # Disable GPU
```

### For GPU-heavy workloads
```yaml
parallel:
  n_workers: 8           # Fewer CPU workers
  use_gpu: true
  trajectory_batch_size: 50  # Larger GPU batches
```

### For memory-constrained scenarios
```yaml
parallel:
  n_workers: 20          # Fewer workers
  max_memory_per_worker: 5.0  # More memory per worker
  trajectory_batch_size: 5    # Smaller GPU batches
```

## Expected Performance

| Workload | Method | Time | Speedup |
|----------|--------|------|---------|
| 100 trajectories | Single-thread | ~800 s | 1× |
| 100 trajectories | 40-worker CPU | ~20 s | 40× |
| 100 trajectories | GPU batch | ~4-8 s | 100-200× |

## Troubleshooting

### GPU not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall JAX with CUDA
pip uninstall jax jaxlib
pip install --upgrade "jax[cuda12]"
```

### Out of memory (GPU)
Reduce `trajectory_batch_size` in `parallel_config.yaml`:
```yaml
parallel:
  trajectory_batch_size: 5  # Reduce from 10
```

### Out of memory (CPU)
Reduce `n_workers` in `parallel_config.yaml`:
```yaml
parallel:
  n_workers: 20  # Reduce from 40
```

## Files Created

```
quantum_simulations_framework_parallel/
├── parallel_config.yaml              # Configuration
├── README_PARALLEL.md                # Full documentation
├── PARALLEL_OPTIMIZATION_SUMMARY.md  # Technical summary
├── benchmark_parallel.py             # Performance testing
├── core/gpu_dynamics.py              # GPU acceleration
├── utils/parallel_utils.py           # Parallel execution
└── reproducibility/main_parallel.py  # Parallel pipeline
```

## Comparison with Original

| Feature | Original | Parallel/GPU |
|---------|----------|--------------|
| Location | `quantum_simulations_framework/` | `quantum_simulations_framework_parallel/` |
| Execution | Single-threaded | 40-worker + GPU |
| 100 trajectories | ~800 s | ~4-20 s |
| GPU support | No | Yes (JAX) |

**Note:** Original codebase is unchanged and still available.

## Next Steps

1. ✅ Run benchmark: `python benchmark_parallel.py`
2. ✅ Run simulation: `python reproducibility/main_parallel.py`
3. ⚙️ Adjust `parallel_config.yaml` based on results
4. 📊 Compare results with original version

## Support

For detailed documentation, see:
- `README_PARALLEL.md` — Full documentation
- `PARALLEL_OPTIMIZATION_SUMMARY.md` — Technical details

---

**Created:** 2026-05-04  
**Optimized for:** Dual Xeon Gold 6136 + RTX A4000
