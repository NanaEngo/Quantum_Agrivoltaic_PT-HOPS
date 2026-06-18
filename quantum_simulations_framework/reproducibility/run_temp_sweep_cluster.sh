#!/bin/bash
#===============================================================================
# Cluster execution script for JPCL temperature sweep (Figure 2a).
# Usage (AGENTS.md):
#   chmod +x run_temp_sweep_cluster.sh
#   ./run_temp_sweep_cluster.sh
# Monitoring:
#   tail -f sweep_cluster.log
#===============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="../sweep_cluster.log"

echo "============================================" | tee -a "$LOG_FILE"
echo "JPCL Temperature Sweep — Cluster Run" | tee -a "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Host:    $(hostname)" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"

# ── Production parameters ──────────────────────────────────────────────────
# L=8, K=2, 100 trajectories (per AGENTS.md)
CONFIG="../config/parameters.yaml"
N_TRAJ=100
N_TRAJ_SWEEP=10

# ── Run the pipeline ────────────────────────────────────────────────────────
mamba run -n MesoHOP-sim python -u main.py \
    --config "$CONFIG" \
    --parallel \
    --skip-audit \
    --n-traj "$N_TRAJ" \
    --n-traj-sweep "$N_TRAJ_SWEEP" \
    2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?

echo "============================================" | tee -a "$LOG_FILE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "Sweep completed successfully: $(date)" | tee -a "$LOG_FILE"
else
    echo "Sweep FAILED (exit code $EXIT_CODE): $(date)" | tee -a "$LOG_FILE"
fi
echo "============================================" | tee -a "$LOG_FILE"

exit $EXIT_CODE
