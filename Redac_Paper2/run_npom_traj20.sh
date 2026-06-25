#!/usr/bin/env bash
# ============================================================================
# R-3: NPoM V=1.2 nm3, n_traj=20, T=295K — Statistical error bars
# Run AFTER R-4 (77K) finishes
# ============================================================================
set -euo pipefail

PROJECT_DIR="$HOME/Redac_Paper2"
FRAMEWORK_DIR="$HOME/quantum_simulations_framework"
PYTHON="$HOME/miniforge3/envs/MesoHOP-sim/bin/python"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RUN_ID="npom_traj20_v1.2_${TIMESTAMP}"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

CONFIG="$PROJECT_DIR/parameters.yaml"
# Always restore from original first
cp "${CONFIG}.bak_ORIGINAL" "$CONFIG"
# Patch: NPoM ON, V=1.2, n_traj=20, T=295K
sed -i \
    -e 's/enabled: false/enabled: true/' \
    -e 's/mode_volume_nm3: 0.8/mode_volume_nm3: 1.2/' \
    -e 's/temperature_k: 77.0/temperature_k: 295.0/' \
    -e 's/n_traj: [0-9]*/n_traj: 20/' \
    "$CONFIG"

echo "[${TIMESTAMP}] R-3: NPoM V=1.2, n_traj=20, T=295K — ${RUN_ID}"

OPENBLAS_NUM_THREADS=1 PYTHONPATH="${PROJECT_DIR}:${FRAMEWORK_DIR}" nohup "$PYTHON" \
    "$PROJECT_DIR/main.py" \
    --log-file "${LOG_DIR}/${RUN_ID}.log" \
    > "${LOG_DIR}/${RUN_ID}_stdout.log" 2>&1 &

SIM_PID=$!
echo "$SIM_PID" > "${LOG_DIR}/${RUN_ID}.pid"
echo "PID: ${SIM_PID}"
echo "Monitor: tail -f ${LOG_DIR}/${RUN_ID}.log"
echo "Restore: cp ${CONFIG}.bak_ORIGINAL ${CONFIG}"
