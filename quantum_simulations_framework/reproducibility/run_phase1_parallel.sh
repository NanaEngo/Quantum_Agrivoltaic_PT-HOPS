#!/bin/bash
# Phase 1 — Lancement parallèle des sweeps restants
# Usage: bash reproducibility/run_phase1_parallel.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_BASE="$FRAMEWORK_DIR/config/server_production.yaml"
PYTHON="$HOME/miniforge3/envs/MesoHOP-sim/bin/python"
MAIN="$FRAMEWORK_DIR/reproducibility/main.py"
RESULTS="$FRAMEWORK_DIR/reproducibility/results"
PARALLEL="--parallel"
N_CONV=${N_CONV:-1}

timestamp() { date +%Y%m%d_%H%M%S; }

cleanup_joblib() {
    local orphans
    orphans=$(ps aux | grep -E "LokyProcess|resource_tracker" | grep -v grep | awk '{print $2}')
    if [ -n "$orphans" ]; then
        kill -9 $orphans 2>/dev/null
        sleep 1
    fi
}

run_sweep_bg() {
    local label="$1"
    local n_traj="$2"
    local config_mod="$3"
    local yaml="$FRAMEWORK_DIR/config/_sweep_${label}.yaml"
    local log="$FRAMEWORK_DIR/reproducibility/sweep_${label}_$(timestamp).log"

    $PYTHON -c "
import yaml, copy
with open('$CONFIG_BASE') as f:
    cfg = yaml.safe_load(f)
cfg['simulation']['n_traj'] = $n_traj
cfg['simulation']['n_traj_temp_sweep'] = $n_traj
$config_mod
with open('$yaml', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False)
"
    echo "[$(timestamp)] Starting $label (N=$n_traj, OMP=24)..."

    OMP_NUM_THREADS=24 MKL_NUM_THREADS=24 NUMBA_NUM_THREADS=24 \
        $PYTHON "$MAIN" --config "$yaml" $PARALLEL --skip-audit --skip-temp-sweep > "$log" 2>&1
    local rc=$?

    for f in "$RESULTS"/fmo_dynamics_*.csv; do
        [ -f "$f" ] && mv "$f" "${f%.csv}_${label}.csv"
    done

    rm -f "$yaml"

    if [ $rc -eq 0 ]; then
        echo "[$(timestamp)] ✅ $label completed"
    else
        echo "[$(timestamp)] ⚠️  $label FAILED (code $rc)"
    fi
}

echo "============================================"
echo "  Phase 1 Parallèle — $(timestamp)"
echo "  K=3, dt=2.0, dt=1.0 avec OMP_NUM_THREADS=24"
echo "============================================"
echo ""

cleanup_joblib

# Lancer K=3 et dt=2.0 en parallèle
run_sweep_bg "K3" $N_CONV "cfg['dynamics']['matsubara_truncation'] = 3" &
PID_K3=$!

run_sweep_bg "dt2" $N_CONV "cfg['dynamics']['time_step'] = 2.0" &
PID_DT2=$!

echo "[$(timestamp)] K3 (PID=$PID_K3) et dt2 (PID=$PID_DT2) lancés en parallèle"
echo ""

# Attendre les deux
wait $PID_K3
echo "[$(timestamp)] K3 terminé"
wait $PID_DT2
echo "[$(timestamp)] dt2 terminé"

cleanup_joblib

# dt=1.0 en dernier (plus long, seul)
run_sweep_bg "dt1" $N_CONV "cfg['dynamics']['time_step'] = 1.0"
echo "[$(timestamp)] dt1 terminé"

echo ""
echo "============================================"
echo "  Phase 1 terminée — $(timestamp)"
echo "============================================"
