#!/bin/bash
# Generic Cluster/Server Execution Script (Background Execution)
# This script ensures the simulation runs in the background even if the terminal is closed.

# Configuration
ENV_NAME="MesoHOP-sim"
MAIN_SCRIPT="reproducibility/main.py"
LOG_FILE="reproducibility_cluster.log"

echo "--------------------------------------------------------"
echo "  Quantum-Enhanced Agrivoltaics: Production Pipeline"
echo "--------------------------------------------------------"

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

# 2. Launch simulation
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
