#!/bin/bash
# Comprehensive sweep for JPCL SI convergence & robustness tables
# Usage: nohup bash reproducibility/run_comprehensive_sweep.sh > sweep_all.log 2>&1 &
# Set N_SWEEP for convergence (1) and N_ROBUST for robustness (20)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_BASE="$FRAMEWORK_DIR/config/server_production.yaml"
PYTHON="$HOME/miniforge3/envs/MesoHOP-sim/bin/python"
MAIN="$FRAMEWORK_DIR/reproducibility/main.py"
RESULTS="$FRAMEWORK_DIR/reproducibility/results"
N_CONV=${N_CONV:-1}
N_ROB=${N_ROBUST:-10}
PARALLEL="--parallel"

timestamp() { date +%Y%m%d_%H%M%S; }

# Kill orphaned joblib/loky workers from previous runs
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
    
    # Build modified YAML using Python
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
    
    # Tag output CSVs
    for f in "$RESULTS"/fmo_dynamics_*.csv; do
        [ -f "$f" ] && mv "$f" "${f%.csv}_${label}.csv"
    done
    
    rm -f "$yaml"
    
    # Kill orphaned workers from this run before next sweep
    cleanup_joblib
    
    if [ $rc -eq 0 ]; then
        echo "[$(timestamp)] ✅ $label completed"
    else
        echo "[$(timestamp)] ⚠️  $label FAILED (code $rc)"
    fi
    return $rc
}

echo "============================================"
echo "  Comprehensive Sweep — $(timestamp)"
echo "  Convergence N=$N_CONV, Robustness N=$N_ROB"
echo "============================================"
echo ""

# Ensure clean slate before starting
cleanup_joblib

# ===== PHASE 1: CONVERGENCE SWEEPS =====
echo "=== PHASE 1: Convergence sweeps (N=$N_CONV) ==="

# L-sweep (vibronic bath)
# L9 désactivé pour optimisation des ressources (convergence atteinte à L=8)
for L in 7; do
    run_sweep "L${L}" $N_CONV "cfg['dynamics']['L_max'] = $L"
done

# K-sweep
for K in 1 3; do
    run_sweep "K${K}" $N_CONV "cfg['dynamics']['matsubara_truncation'] = $K"
done

# dt-sweep
for dt in 2.0 1.0 0.1; do
    run_sweep "dt${dt}" $N_CONV "cfg['dynamics']['time_step'] = $dt"
done

# ===== PHASE 2: ROBUSTNESS SWEEPS =====
echo ""
echo "=== PHASE 2: Robustness sweeps (N=$N_ROB) ==="

# Temperature sweep
for T in 285 290 300 305 310; do
    run_sweep "T${T}" $N_ROB "cfg['bath']['temperature'] = float($T)"
done

# Bath sensitivity: λ_D
for lam in 28 42; do
    run_sweep "lambda${lam}" $N_ROB "cfg['bath']['reorganization_energy'] = float($lam)"
done

# Bath sensitivity: γ_D
for gam in 40 60; do
    run_sweep "gamma${gam}" $N_ROB "cfg['bath']['drude_cutoff'] = float($gam)"
done

# Filter band center variations
run_sweep "filt770_820" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [770.0, 820.0]"
run_sweep "filt730_820" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [730.0, 820.0]"
run_sweep "filt750_800" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [750.0, 800.0]"

# Filter bandwidth (emulates chirp tolerance)
run_sweep "bw50" $N_ROB "cfg['spectral_filter']['bandwidth_cm'] = 50.0"
run_sweep "bw200" $N_ROB "cfg['spectral_filter']['bandwidth_cm'] = 200.0"

# Single-band negative controls
run_sweep "single700" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [700.0]; cfg['spectral_filter']['bandwidth_cm'] = 100.0"
run_sweep "single850" $N_ROB "cfg['spectral_filter']['band_centers_nm'] = [850.0]; cfg['spectral_filter']['bandwidth_cm'] = 100.0"

echo ""
echo "============================================"
echo "  All sweeps completed — $(timestamp)"
echo "============================================"
