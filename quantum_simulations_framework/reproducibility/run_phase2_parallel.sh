#!/bin/bash
# Phase 2 Parallel — 4 sweeks simultanés pour ≥60 GiB RAM
# Usage: nohup bash reproducibility/run_phase2_parallel.sh > ~/phase2_parallel.log 2>&1 &

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_BASE="$FRAMEWORK_DIR/config/server_production.yaml"
PYTHON="$HOME/miniforge3/envs/MesoHOP-sim/bin/python"
MAIN="$FRAMEWORK_DIR/reproducibility/main.py"
RESULTS="$FRAMEWORK_DIR/reproducibility/results"
N=5
PARALLEL="--parallel"
OMP_NUM_THREADS=12
MKL_NUM_THREADS=12
export OMP_NUM_THREADS MKL_NUM_THREADS

timestamp() { date +%Y%m%d_%H%M%S; }

run_one() {
    local label="$1"
    local yaml="$FRAMEWORK_DIR/config/_sweep_${label}.yaml"
    local log="$FRAMEWORK_DIR/reproducibility/sweep_${label}_$(timestamp).log"

    $PYTHON -c "
import yaml
with open('$CONFIG_BASE') as f:
    cfg = yaml.safe_load(f)
cfg['dynamics']['L_max'] = 7
cfg['simulation']['n_traj'] = $N
cfg['simulation']['n_traj_temp_sweep'] = $N
cfg['simulation']['n_disorder_samples'] = 1
$2
with open('$yaml', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False)
"
    echo "[$(timestamp)] Starting $label (L=7, N=$N)..."
    $PYTHON "$MAIN" --config "$yaml" $PARALLEL --skip-audit --skip-temp-sweep >> "$log" 2>&1
    local rc=$?
    for f in "$RESULTS"/fmo_dynamics_*.csv; do
        [ -f "$f" ] && mv "$f" "${f%.csv}_${label}.csv"
    done
    rm -f "$yaml"
    echo "[$(timestamp)] $label → code $rc"
    return $rc
}

cleanup() {
    local orphans
    orphans=$(ps aux | grep -E "LokyProcess|resource_tracker" | grep -v grep | awk '{print $2}' || true)
    if [ -n "$orphans" ]; then
        kill -9 $orphans 2>/dev/null || true
    fi
}

echo "============================================"
echo "  Phase 2 Parallèle — $(timestamp)"
echo "  4 runs simultanés, N=$N, L=7, ≥60 GiB visé"
echo "============================================"
echo ""

# Batch 1: 4 températures en parallèle
echo "--- Batch 1: T290 + T300 + T305 + T310 ---"
cleanup
run_one "T290" "cfg['bath']['temperature'] = 290.0" &
PID1=$!
run_one "T300" "cfg['bath']['temperature'] = 300.0" &
PID2=$!
run_one "T305" "cfg['bath']['temperature'] = 305.0" &
PID3=$!
run_one "T310" "cfg['bath']['temperature'] = 310.0" &
PID4=$!
wait $PID1 $PID2 $PID3 $PID4 || true
echo "--- Batch 1 terminé ---"
cleanup

# Batch 2: Bath λ_D + γ_D (4 runs)
echo "--- Batch 2: λ=28, λ=42, γ=40, γ=60 ---"
run_one "lambda28" "cfg['bath']['reorganization_energy'] = 28.0" &
PID1=$!
run_one "lambda42" "cfg['bath']['reorganization_energy'] = 42.0" &
PID2=$!
run_one "gamma40" "cfg['bath']['drude_cutoff'] = 40.0" &
PID3=$!
run_one "gamma60" "cfg['bath']['drude_cutoff'] = 60.0" &
PID4=$!
wait $PID1 $PID2 $PID3 $PID4 || true
echo "--- Batch 2 terminé ---"
cleanup

# Batch 3: Filter centers (3 runs) + bandwidth (2 runs)
echo "--- Batch 3: filtres + bandwidth ---"
run_one "filt770_820" "cfg['spectral_filter']['band_centers_nm'] = [770.0, 820.0]" &
PID1=$!
run_one "filt730_820" "cfg['spectral_filter']['band_centers_nm'] = [730.0, 820.0]" &
PID2=$!
run_one "filt750_800" "cfg['spectral_filter']['band_centers_nm'] = [750.0, 800.0]" &
PID3=$!
run_one "bw50" "cfg['spectral_filter']['bandwidth_cm'] = 50.0" &
PID4=$!
wait $PID1 $PID2 $PID3 $PID4 || true

run_one "bw200" "cfg['spectral_filter']['bandwidth_cm'] = 200.0" &
PID5=$!
run_one "single700" "cfg['spectral_filter']['band_centers_nm'] = [700.0]; cfg['spectral_filter']['bandwidth_cm'] = 100.0" &
PID6=$!
run_one "single850" "cfg['spectral_filter']['band_centers_nm'] = [850.0]; cfg['spectral_filter']['bandwidth_cm'] = 100.0" &
PID7=$!
wait $PID5 $PID6 $PID7 || true
echo "--- Batch 3 terminé ---"
cleanup

echo ""
echo "============================================"
echo "  Phase 2 terminée — $(timestamp)"
echo "============================================"
