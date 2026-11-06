#!/bin/bash
# Phase 1 suite: K-sweep + dt-sweep (L7 déjà fait le 17 juin)
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_BASE="$FRAMEWORK_DIR/config/server_production.yaml"
PYTHON="$HOME/miniforge3/envs/MesoHOP-sim/bin/python"
MAIN="$FRAMEWORK_DIR/reproducibility/main.py"
RESULTS="$FRAMEWORK_DIR/reproducibility/results"
N_CONV=${N_CONV:-1}
PARALLEL="--parallel"

timestamp() { date +%Y%m%d_%H%M%S; }

cleanup_joblib() {
    local orphans
    orphans=$(ps aux | grep -E "LokyProcess|resource_tracker" | grep -v grep | awk '{print $2}')
    if [ -n "$orphans" ]; then
        echo "[$(timestamp)] Cleaning $(echo "$orphans" | wc -l) orphan joblib worker(s)..."
        kill -9 $orphans 2>/dev/null
        sleep 1
    fi
}

run_sweep() {
    local label="$1"
    local n_traj="$2"
    local yaml="$FRAMEWORK_DIR/config/_sweep_${label}.yaml"
    local log="$FRAMEWORK_DIR/reproducibility/sweep_${label}_$(timestamp).log"

    $PYTHON -c "
import yaml, copy
with open('$CONFIG_BASE') as f:
    cfg = yaml.safe_load(f)
cfg['simulation']['n_traj'] = $n_traj
cfg['simulation']['n_traj_temp_sweep'] = $n_traj
$3
with open('$yaml', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False)
"
    echo "[$(timestamp)] Starting $label (N=$n_traj)..."
    $PYTHON "$MAIN" --config "$yaml" $PARALLEL --skip-audit --skip-temp-sweep >> "$log" 2>&1
    local rc=$?

    for f in "$RESULTS"/fmo_dynamics_*.csv; do
        [ -f "$f" ] && mv "$f" "${f%.csv}_${label}.csv"
    done

    rm -f "$yaml"
    cleanup_joblib

    if [ $rc -eq 0 ]; then
        echo "[$(timestamp)] ✅ $label completed"
    else
        echo "[$(timestamp)] ⚠️  $label FAILED (code $rc)"
    fi
    return $rc
}

echo "============================================"
echo "  Phase 1 (suite) — $(timestamp)"
echo "  K-sweep + dt-sweep (L7 déjà fait)"
echo "============================================"
echo ""

cleanup_joblib

# K-sweep
for K in 1 3; do
    run_sweep "K${K}" $N_CONV "cfg['dynamics']['matsubara_truncation'] = $K"
done

# dt-sweep
for dt in 2.0 1.0; do
    run_sweep "dt${dt}" $N_CONV "cfg['dynamics']['time_step'] = $dt"
done

echo ""
echo "============================================"
echo "  Phase 1 completed — $(timestamp)"
echo "============================================"
