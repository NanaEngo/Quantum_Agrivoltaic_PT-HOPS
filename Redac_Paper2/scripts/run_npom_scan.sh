#!/bin/bash
# NPoM volume sensitivity scan
# Usage: bash run_npom_scan.sh
# Runs 7 volumes sequentially, ~40 min each = ~4.7 hours total

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VOLUMES=(0.2 0.4 0.6 0.8 1.0 1.2 1.4)
RESULTS="npom_scan_results.csv"
echo "vol_nm3,phi_FT,elapsed_s,status" > "$RESULTS"

export PYTHONPATH="$SCRIPT_DIR:$HOME/quantum_simulations_framework"
export OPENBLAS_NUM_THREADS=1

for V in "${VOLUMES[@]}"; do
    echo "=== NPoM volume: $V nm³ ==="
    # Modify YAML safely via Python
    ~/miniforge3/envs/MesoHOP-sim/bin/python -c "
import yaml
with open('parameters.yaml') as f:
    d = yaml.safe_load(f)
d['quantum']['npom']['enabled'] = True
d['quantum']['fmo']['mode_volume_nm3'] = $V
with open('parameters.yaml', 'w') as f:
    yaml.dump(d, f, default_flow_style=False)
"
    START=$(date +%s)
    nohup ~/miniforge3/envs/MesoHOP-sim/bin/python main.py \
        --log-file "scan_vol_${V}.log" > "scan_vol_${V}_stdout.log" 2>&1
    STATUS=$?
    END=$(date +%s)
    ELAPSED=$((END - START))
    YIELD=$(grep -oP "\(Phi_FT\):\s*\K[0-9.]+" "scan_vol_${V}.log" 2>/dev/null || echo "FAILED")
    echo "$V,${YIELD},${ELAPSED},${STATUS}" >> "$RESULTS"
    echo "  → Yield: ${YIELD} (${ELAPSED}s, exit=${STATUS})"
done

echo "Scan complete. Results in $RESULTS"
