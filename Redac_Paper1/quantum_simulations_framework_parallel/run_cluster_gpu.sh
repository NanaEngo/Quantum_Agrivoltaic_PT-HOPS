#!/bin/bash
# Cluster/Server Execution Script (Background Execution)
# Activates $HOME/VirtualEnv, checks GPU, then launches main.py in the background.

MAIN_SCRIPT="reproducibility/main.py"
LOG_FILE="reproducibility_cluster.log"
GPU_ID="0"

export CUDA_VISIBLE_DEVICES="$GPU_ID"

echo "--------------------------------------------------------"
echo "  Quantum-Enhanced Agrivoltaics: Production Pipeline"
echo "--------------------------------------------------------"
echo "  GPU target: CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"

# Activate virtual environment
VENV="$HOME/VirtualEnv/bin/activate"
if [ -f "$VENV" ]; then
    echo "  ✅ Activating virtual environment: $VENV"
    source "$VENV"
else
    echo "  ❌ Virtual environment not found at $VENV"
    exit 1
fi

# Verify Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found in virtual environment"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    echo "🔍 NVIDIA GPU status:"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
else
    echo "⚠️  nvidia-smi not found — continuing without GPU check"
fi

# Python-side GPU library check
python3 - <<'PY'
import importlib.util
for lib in ("cupy", "torch", "jax"):
    if importlib.util.find_spec(lib) is not None:
        try:
            if lib == "cupy":
                import cupy as cp
                name = cp.cuda.runtime.getDeviceProperties(0)["name"]
                name = name.decode() if isinstance(name, bytes) else name
                print(f"✅ CuPy GPU: {name}")
            elif lib == "torch":
                import torch
                print(f"✅ PyTorch CUDA available: {torch.cuda.is_available()}")
            elif lib == "jax":
                import jax
                print(f"✅ JAX devices: {jax.devices()}")
        except Exception as e:
            print(f"⚠️  {lib} detected but check failed: {e}")
    else:
        print(f"ℹ️  {lib} not installed")
PY

# Prevent JAX from pre-allocating GPU/RAM at import time
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_MEM_FRACTION=0.33   # cap JAX at 1/3 of available RAM if it does allocate

# Launch simulation
echo "🚀 Launching $MAIN_SCRIPT in background..."
nohup python3 -u "$MAIN_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!

echo "✅ Job submitted (PID: $PID)"
echo "📂 Log file: $LOG_FILE"
echo "📊 Monitor: tail -f $LOG_FILE"
echo "--------------------------------------------------------"
