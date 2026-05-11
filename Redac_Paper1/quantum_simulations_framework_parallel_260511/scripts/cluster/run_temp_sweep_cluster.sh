#!/bin/bash
# run_temp_sweep_cluster.sh
# Production Execution Script for Server/Cluster (Parallel Mode)

ENV_NAME="MesoHOP-sim"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/run_temp_sweep_only.py"
LOG_FILE="$SCRIPT_DIR/logs/sweep_cluster.log"

mkdir -p "$SCRIPT_DIR/logs"

echo "--------------------------------------------------------"
echo "  JPCL Figure 2: Server-Side Temperature Sweep"
echo "--------------------------------------------------------"

# 1. Check for mamba/conda
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
elif command -v conda &> /dev/null; then
    CONDA_CMD="conda"
else
    CONDA_CMD=""
fi

# 2. Launch simulation with --parallel flag
# This will use the hardware-aware n_jobs logic (Memory/CPU limited)
echo "🚀 Launching in Parallel Mode (Resume enabled)..."
if [ -n "$CONDA_CMD" ]; then
    nohup $CONDA_CMD run -n $ENV_NAME python -u "$PYTHON_SCRIPT" --parallel > "$LOG_FILE" 2>&1 &
else
    nohup python -u "$PYTHON_SCRIPT" --parallel > "$LOG_FILE" 2>&1 &
fi

PID=$!
echo "✅ Job submitted to background (PID: $PID)."
echo "📂 Log file: $LOG_FILE"
echo "📊 Monitoring: tail -f $LOG_FILE"
echo "--------------------------------------------------------"
