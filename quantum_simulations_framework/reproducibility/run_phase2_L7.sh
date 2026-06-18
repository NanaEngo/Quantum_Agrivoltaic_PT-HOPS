#!/bin/bash
# Phase 2 Robustness Sweeps — L=7, N=10, parallel-safe with Phase 1
# Usage: nohup bash reproducibility/run_phase2_L7.sh > ~/phase2_L7.log 2>&1 &
#
# No cleanup_joblib: avoids killing Phase 1 LokyProcess workers.
# Use MEMORY_FRACTION_LIMIT=0.75 to target ≥60 GiB RAM.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_BASE="$FRAMEWORK_DIR/config/server_production.yaml"
PYTHON="$HOME/miniforge3/envs/MesoHOP-sim/bin/python"
MAIN="$FRAMEWORK_DIR/reproducibility/main.py"
RESULTS="$FRAMEWORK_DIR/reproducibility/results"
N_ROB=10
PARALLEL="--parallel"
OMP_NUM_THREADS=24
MKL_NUM_THREADS=24
export OMP_NUM_THREADS MKL_NUM_THREADS

timestamp() { date +%Y%m%d_%H%M%S; }

run_sweep() {
    local label="$1"
    local n_traj="$2"
    local yaml="$FRAMEWORK_DIR/config/_sweep_${label}.yaml"
    local log="$FRAMEWORK_DIR/reproducibility/sweep_${label}_$(timestamp).log"

    # Build modified YAML (L=7 + sweep parameter)
    # n_disorder_samples=1 to skip costly disorder sampling in Phase 2
    $PYTHON -c "
import yaml, copy
with open('$CONFIG_BASE') as f:
    cfg = yaml.safe_load(f)
cfg['dynamics']['L_max'] = 7
cfg['simulation']['n_traj'] = $n_traj
cfg['simulation']['n_traj_temp_sweep'] = $n_traj
cfg['simulation']['n_disorder_samples'] = 1
$3
with open('$yaml', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False)
"
    echo "[$(timestamp)] Starting $label (L=7, N=$n_traj)..."
    $PYTHON "$MAIN" --config "$yaml" $PARALLEL --skip-audit --skip-temp-sweep >> "$log" 2>&1
    local rc=$?

    # Tag output CSVs
    for f in "$RESULTS"/fmo_dynamics_*.csv; do
        [ -f "$f" ] && mv "$f" "${f%.csv}_${label}.csv"
    done

    rm -f "$yaml"

    if [ $rc -eq 0 ]; then
        echo "[$(timestamp)] ✅ $label completed"
    else
        echo "[$(timestamp)] ⚠️  $label FAILED (code $rc)"
    fi
    return $rc
}

echo "============================================"
echo "  Phase 2 Robustness Sweeps — $(timestamp)"
echo "  L=7, N=$N_ROB, MEMORY_FRACTION=0.75"
echo "  Running alongside Phase 1 (no cleanup)"
echo "============================================"
echo ""

# ===== TEMPERATURE SWEEP =====
for T in 285 290 300 305 310; do
    run_sweep "T${T}" $N_ROB "cfg['bath']['temperature'] = float($T)"
done

# ===== BATH SENSITIVITY: λ_D (reorganization energy) =====
for lam in 28 42; do
    run_sweep "lambda${lam}" $N_ROB "cfg['bath']['reorganization_energy'] = float($lam)"
done

# ===== BATH SENSITIVITY: γ_D (Drude cutoff) =====
for gam in 40 60; do
    run_sweep "gamma${gam}" $N_ROB "cfg['bath']['drude_cutoff'] = float($gam)"
done

# ===== FILTER BAND CENTER VARIATIONS =====
run_sweep "filt770_820" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [770.0, 820.0]"
run_sweep "filt730_820" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [730.0, 820.0]"
run_sweep "filt750_800" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [750.0, 800.0]"

# ===== FILTER BANDWIDTH (chirp/pulse-width tolerance) =====
run_sweep "bw50" $N_ROB "cfg['spectral_filter']['bandwidth_cm'] = 50.0"
run_sweep "bw200" $N_ROB "cfg['spectral_filter']['bandwidth_cm'] = 200.0"

# ===== SINGLE-BAND NEGATIVE CONTROLS =====
run_sweep "single700" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [700.0]; cfg['spectral_filter']['bandwidth_cm'] = 100.0"
run_sweep "single850" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [850.0]; cfg['spectral_filter']['bandwidth_cm'] = 100.0"

echo ""
echo "============================================"
echo "  Phase 2 completed — $(timestamp)"
echo "============================================"
