#!/bin/bash
# Cluster/Server Execution Script (Background Execution)
# Activates $HOME/VirtualEnv, checks GPU, then launches main.py in the background.
#
# Usage (from any directory):
#   bash /path/to/run_cluster_gpu.sh
#   bash /path/to/run_cluster_gpu.sh --config config/server_parameters.yaml

# ── Fix 1: anchor all paths to the script's own directory ─────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_DIR="$SCRIPT_DIR/quantum_simulations_framework_parallel_260512"
MAIN_SCRIPT="$FRAMEWORK_DIR/reproducibility/main.py"

# ── Fix 2: log goes inside the framework's log directory ──────────────────────
LOG_DIR="$FRAMEWORK_DIR/reproducibility/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/cluster_gpu_$(date +%Y%m%d_%H%M%S).log"
PID_FILE="$LOG_DIR/cluster_gpu.pid"

GPU_ID="0"
export CUDA_VISIBLE_DEVICES="$GPU_ID"

# ── Fix 4: align JAX memory fraction with parallel_config.yaml (0.9) ──────────
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_MEM_FRACTION=0.90   # matches gpu_memory_fraction in parallel_config.yaml

echo "--------------------------------------------------------"
echo "  Quantum-Enhanced Agrivoltaics: Production Pipeline"
echo "--------------------------------------------------------"
echo "  Script dir : $SCRIPT_DIR"
echo "  Framework  : $FRAMEWORK_DIR"
echo "  GPU target : CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"

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

# ── Fix 3: pass --config so server_parameters.yaml is used when specified ─────
# Default: main.py auto-selects parameters.yaml (production, L=8).
# Override: bash run_cluster_gpu.sh --config config/server_parameters.yaml
EXTRA_ARGS="$*"

# Launch simulation
echo "🚀 Launching $MAIN_SCRIPT in background..."
nohup python3 -u "$MAIN_SCRIPT" --parallel $EXTRA_ARGS > "$LOG_FILE" 2>&1 &
PID=$!

# ── Fix 5: persist PID to file for clean job management ───────────────────────
echo "$PID" > "$PID_FILE"

echo "✅ Job submitted (PID: $PID)"
echo "📂 Log file : $LOG_FILE"
echo "📄 PID file : $PID_FILE"
echo "📊 Monitor  : tail -f $LOG_FILE"
echo "🛑 Kill job : kill \$(cat $PID_FILE)"
echo "--------------------------------------------------------"
