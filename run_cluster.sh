#!/bin/bash
# Generic Cluster/Server Execution Script (Background Execution)
# This script ensures the simulation runs in the background even if the terminal is closed.

# Configuration
ENV_NAME="MesoHOP-sim"
MAIN_SCRIPT="Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py"
LOG_FILE="reproducibility_cluster.log"

echo "--------------------------------------------------------"
echo "  Quantum-Enhanced Agrivoltaics: Production Pipeline"
echo "--------------------------------------------------------"

# 1. Check for mamba/conda
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
elif command -v conda &> /dev/null; then
    CONDA_CMD="conda"
else
    echo "⚠️ Warning: Neither mamba nor conda found. Assuming environment is pre-activated."
    CONDA_CMD=""
fi

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
