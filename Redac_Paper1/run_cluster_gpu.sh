#!/bin/bash
# Generic Cluster/Server Execution Script (Background Execution)
# This script ensures the simulation runs in the background even if the terminal is closed.
# GPU-ready version: keeps the original virtual environment activation logic,
# checks NVIDIA/CUDA visibility, and exposes GPU 0 to the Python process.

# Configuration
ENV_NAME="MesoHOP-sim"
MAIN_SCRIPT="reproducibility/main.py"
LOG_FILE="reproducibility_cluster.log"
GPU_ID="0"

# Expose the selected GPU to the process
export CUDA_VISIBLE_DEVICES="$GPU_ID"

echo "--------------------------------------------------------"
echo "  Quantum-Enhanced Agrivoltaics: Production Pipeline"
echo "--------------------------------------------------------"
echo "  GPU target: CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"

# Try multiple possible venv locations
VENV_PATHS=(
    "$HOME/VirtualEnv/bin/activate"
    "$HOME/venv/bin/activate"
    "$HOME/.venv/bin/activate"
)

ACTIVATED=false
for venv in "${VENV_PATHS[@]}"; do
    if [ -f "$venv" ]; then
        echo "  ✅ Activating virtual environment: $venv"
        source "$venv"
        ACTIVATED=true
        break
    fi
done

if [ "$ACTIVATED" = false ]; then
    echo "  ⚠️  No virtual environment found. Trying with system Python..."
    echo "  Checked: ${VENV_PATHS[*]}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi
echo "✅ Python3 available"

# Check NVIDIA GPU visibility
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found. NVIDIA driver/CUDA runtime may not be available."
    exit 1
fi

echo "🔍 NVIDIA GPU status:"
nvidia-smi
if [ $? -ne 0 ]; then
    echo "ERROR: nvidia-smi failed. GPU is not accessible."
    exit 1
fi

# Optional Python-side GPU checks.
# These checks do not force MesoHOPS to use the GPU, but they confirm whether common
# GPU libraries can see CUDA from inside the selected Python environment.
echo "🔍 Python GPU library checks:"
python3 - <<'PY'
import importlib.util

checked_any = False

if importlib.util.find_spec("cupy") is not None:
    checked_any = True
    try:
        import cupy as cp
        props = cp.cuda.runtime.getDeviceProperties(0)
        name = props["name"].decode() if isinstance(props["name"], bytes) else props["name"]
        print(f"✅ CuPy GPU OK: {name}")
    except Exception as e:
        print(f"⚠️ CuPy detected but GPU check failed: {e}")
else:
    print("ℹ️ CuPy not installed in this Python environment")

if importlib.util.find_spec("torch") is not None:
    checked_any = True
    try:
        import torch
        available = torch.cuda.is_available()
        print(f"✅ PyTorch CUDA available: {available}")
        if available:
            print(f"✅ PyTorch GPU: {torch.cuda.get_device_name(0)}")
    except Exception as e:
        print(f"⚠️ PyTorch detected but CUDA check failed: {e}")
else:
    print("ℹ️ PyTorch not installed in this Python environment")

if importlib.util.find_spec("jax") is not None:
    checked_any = True
    try:
        import jax
        devices = jax.devices()
        print(f"✅ JAX devices: {devices}")
    except Exception as e:
        print(f"⚠️ JAX detected but device check failed: {e}")
else:
    print("ℹ️ JAX not installed in this Python environment")

if not checked_any:
    print("⚠️ No common GPU Python backend detected: CuPy, PyTorch, or JAX.")
PY

# 2. Launch simulation
# Note: this script exposes the GPU and checks CUDA visibility, but actual GPU use
# still depends on the Python/MesoHOPS code using a GPU-capable backend.
if [ -n "$CONDA_CMD" ]; then
    echo "🚀 Launching via $CONDA_CMD run..."
    nohup $CONDA_CMD run -n $ENV_NAME python -u $MAIN_SCRIPT > $LOG_FILE 2>&1 &
else
    echo "🚀 Launching via native python..."
    nohup python -u $MAIN_SCRIPT > $LOG_FILE 2>&1 &
fi

# 3. Finalize
PID=$!
echo "✅ Job submitted to background (PID: $PID)."
echo "📂 Log file: $LOG_FILE"
echo "📊 Monitoring: tail -f $LOG_FILE"
echo "--------------------------------------------------------"
