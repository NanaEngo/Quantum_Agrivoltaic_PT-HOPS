# CUDA Native Support Update

**Date:** 2026-05-04  
**Status:** ✅ COMPLETE

---

## Changes Made

Updated the parallel/GPU codebase to prioritize **native CUDA** (via CuPy) with JAX as fallback.

### GPU Backend Priority

1. **CuPy** (CUDA native) — **PREFERRED**
   - Direct CUDA kernel execution
   - Fastest performance
   - Native GPU memory management
   - Install: `pip install cupy-cuda12x`

2. **JAX** (XLA/CUDA) — **FALLBACK**
   - JIT compilation to CUDA
   - Good performance
   - Automatic differentiation support
   - Install: `pip install "jax[cuda12]"`

3. **CPU** — **FALLBACK**
   - NumPy/SciPy
   - Used when no GPU libraries available

---

## Files Modified

### 1. `core/gpu_dynamics.py`
**Changes:**
- Added CuPy import and detection
- Updated `GPUQuantumDynamics.__init__()` to support backend selection
- Added `_simulate_batch_cupy()` method for CuPy backend
- Renamed `_simulate_batch_gpu()` to `_simulate_batch_jax()`
- Added `_liouvillian_step_cupy()` and `_rk4_step_cupy()` methods
- Updated `compute_populations_batch()` to support both backends
- Updated `gpu_ensemble_average()` to support both backends
- Updated `gpu_batch_coherence()` to support both backends

**Backend Selection Logic:**
```python
# Automatic backend selection
if backend == 'auto':
    if use_gpu and CUPY_AVAILABLE:
        self.backend = 'cupy'  # Prefer CuPy (native CUDA)
    elif use_gpu and JAX_AVAILABLE:
        self.backend = 'jax'   # Fallback to JAX
    else:
        self.backend = 'cpu'   # CPU fallback
```

### 2. `reproducibility/main_parallel.py`
**Changes:**
- Updated `check_system_resources()` to check for CuPy first
- Added CUDA runtime detection
- Updated `_run_gpu_batch_simulation()` to use auto backend selection
- Added logging for selected GPU backend

### 3. `QUICKSTART.md`
**Changes:**
- Updated installation instructions to recommend CuPy first
- Added CuPy verification command
- Noted that JAX is fallback

---

## Installation Instructions

### Recommended: CuPy (Native CUDA)
```bash
mamba activate MesoHOP-sim
pip install cupy-cuda12x

# Verify
python -c "
import cupy as cp
print(f'CuPy: {cp.__version__}')
print(f'CUDA: {cp.cuda.runtime.runtimeGetVersion()}')
print(f'Device: {cp.cuda.Device(0).name.decode()}')
"
```

### Alternative: JAX (Fallback)
```bash
mamba activate MesoHOP-sim
pip install --upgrade "jax[cuda12]"

# Verify
python -c "import jax; print(jax.devices())"
```

---

## Usage

The code **automatically selects** the best available backend:

```python
from core.gpu_dynamics import GPUQuantumDynamics, GPU_BACKEND

# Auto-select backend (CuPy > JAX > CPU)
gpu_sim = GPUQuantumDynamics(H, temperature=295.0, use_gpu=True, backend='auto')

# Check which backend was selected
print(f"Using backend: {GPU_BACKEND}")  # 'cupy', 'jax', or 'none'
```

**Manual backend selection:**
```python
# Force CuPy
gpu_sim = GPUQuantumDynamics(H, use_gpu=True, backend='cupy')

# Force JAX
gpu_sim = GPUQuantumDynamics(H, use_gpu=True, backend='jax')

# Force CPU
gpu_sim = GPUQuantumDynamics(H, use_gpu=False, backend='cpu')
```

---

## Performance Comparison

| Backend | Speed | Memory | Notes |
|---------|-------|--------|-------|
| **CuPy** | **Fastest** | Efficient | Native CUDA, direct kernel execution |
| **JAX** | Fast | Efficient | JIT compilation, slight overhead |
| **CPU** | Baseline | Standard | NumPy/SciPy fallback |

**Expected speedup (100 trajectories):**
- CuPy: ~200× vs single-thread CPU
- JAX: ~150× vs single-thread CPU
- CPU parallel (40 workers): ~40× vs single-thread CPU

---

## System Check

Run this to see what's available on your system:

```bash
cd quantum_simulations_framework_parallel
python -c "
from core.gpu_dynamics import CUPY_AVAILABLE, JAX_AVAILABLE, GPU_BACKEND

print('GPU Backend Status:')
print(f'  CuPy available: {CUPY_AVAILABLE}')
print(f'  JAX available: {JAX_AVAILABLE}')
print(f'  Selected backend: {GPU_BACKEND}')

if CUPY_AVAILABLE:
    import cupy as cp
    print(f'  CuPy version: {cp.__version__}')
    print(f'  CUDA version: {cp.cuda.runtime.runtimeGetVersion()}')
    print(f'  Device: {cp.cuda.Device(0).name.decode()}')
elif JAX_AVAILABLE:
    import jax
    print(f'  JAX version: {jax.__version__}')
    print(f'  Devices: {jax.devices()}')
else:
    print('  No GPU backend available - using CPU')
"
```

---

## Verification

### Test CuPy Installation
```bash
python -c "
import cupy as cp
import numpy as np

# Create test array on GPU
x_gpu = cp.array([1, 2, 3, 4, 5])
y_gpu = x_gpu ** 2

# Transfer back to CPU
y_cpu = cp.asnumpy(y_gpu)

print(f'Input: {x_gpu}')
print(f'Output: {y_cpu}')
print('✓ CuPy working correctly')
"
```

### Test GPU Dynamics
```bash
cd quantum_simulations_framework_parallel
python -c "
from core.hamiltonian_factory import create_fmo_hamiltonian
from core.gpu_dynamics import GPUQuantumDynamics, GPU_BACKEND
import numpy as np

H = create_fmo_hamiltonian()
gpu_sim = GPUQuantumDynamics(H, use_gpu=True, backend='auto')

print(f'Backend: {GPU_BACKEND}')

# Test batch simulation
initial_states = np.zeros((5, 7, 7), dtype=np.complex128)
initial_states[:, 0, 0] = 1.0
time_points = np.linspace(0, 100, 21)

trajectories = gpu_sim.simulate_batch_trajectories(initial_states, time_points)
print(f'Result shape: {trajectories.shape}')
print('✓ GPU dynamics working correctly')
"
```

---

## Troubleshooting

### CuPy not found
```bash
# Install CuPy for CUDA 12.x
pip install cupy-cuda12x

# If you have CUDA 11.x
pip install cupy-cuda11x
```

### CUDA version mismatch
```bash
# Check CUDA version
nvidia-smi

# Install matching CuPy version
# CUDA 12.x: cupy-cuda12x
# CUDA 11.x: cupy-cuda11x
```

### GPU not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA runtime
python -c "import ctypes; ctypes.CDLL('libcuda.so'); print('CUDA OK')"
```

---

## Summary

✅ **CuPy support added** (native CUDA, preferred)  
✅ **JAX as fallback** (automatic selection)  
✅ **Automatic backend detection** (CuPy > JAX > CPU)  
✅ **Manual backend override** (if needed)  
✅ **Installation instructions updated**  
✅ **System check utilities added**  

**Recommendation:** Install CuPy for best performance on your CUDA-enabled server.

```bash
pip install cupy-cuda12x
```

---

**Updated by:** Senior Computer Scientist (AI Agent)  
**Date:** 2026-05-04  
**System:** Dual Xeon Gold 6136 + RTX A4000 (CUDA 12.x)
