#!/bin/bash
# run_production.sh
# PenavoraServer Production Execution Script
# Usage: ./run_production.sh [--skip-audit] [--parallel]
#   --skip-audit : Skip convergence audit (default for production)
#   --parallel   : Enable parallel batch execution (default)

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MAIN_SCRIPT="reproducibility/main.py"
LOG_FILE="$HOME/production_run.log"
PYTHON="$HOME/miniforge3/envs/MesoHOP-sim/bin/python"
PARAMS="$BASE_DIR/parameters.yaml"

# NVML driver mismatch has been fixed; GPU auto-detection is now safe.
# Previously set NUMBA_DISABLE_CUDA=1 + CUDA_VISIBLE_DEVICES="" to bypass SIGSEGV.
# Numba/JAX will auto-detect CUDA and fall back to CPU if unavailable.

# Default flags
FLAGS="--skip-audit"
if [ "$1" = "--audit" ]; then
    FLAGS=""
fi

echo "========================================================"
echo "  PenavoraServer — Production Simulation"
echo "  Date: $(date)"
echo "  Host: $(hostname)"
echo "  CPUs: $(nproc)"
echo "  RAM:  $(free -h | awk '/^Mem:/{print $2}')"
echo "  Env:  $PYTHON"
echo "========================================================"

# Vérifier l'environnement
if [ ! -f "$PYTHON" ]; then
    echo "ERROR: Python introuvable: $PYTHON"
    exit 1
fi
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "ERROR: main.py introuvable dans $BASE_DIR"
    exit 1
fi
if [ ! -f "$PARAMS" ]; then
    echo "ERROR: parameters.yaml introuvable dans $BASE_DIR"
    exit 1
fi

echo "  ✅ Env: $($PYTHON --version)"
echo "  ✅ Config: $PARAMS"
echo ""

# Lancer la simulation
cd "$BASE_DIR"
echo "🚀 Lancement: $MAIN_SCRIPT $FLAGS"
echo "📂 Log: $LOG_FILE"
echo ""

nohup $PYTHON -u "$MAIN_SCRIPT" $FLAGS > "$LOG_FILE" 2>&1 &

PID=$!
echo "✅ PID: $PID"
echo "📊 Monitorer: tail -f $LOG_FILE"
echo "📊 Résumé:   grep -E 'batch|ERROR|WARNING|MAE' $LOG_FILE"
echo "🛑 Arrêter:   pkill -f 'main.py'"
echo "========================================================"
