#!/bin/bash
#SBATCH --job-name=npom_scan_n20
#SBATCH --output=/home/nanaengo/Redac_Paper2/logs/npom_scan_%j.log
#SBATCH --error=/home/nanaengo/Redac_Paper2/logs/npom_scan_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=80G
#SBATCH --time=72:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

PROJECT_DIR=/home/nanaengo/Redac_Paper2
FRAMEWORK_DIR=/home/nanaengo/quantum_simulations_framework
PYTHON=/home/nanaengo/miniforge3/envs/MesoHOP-sim/bin/python

export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OMP_NUM_THREADS=1
export PYTHONUNBUFFERED=1

cd ${PROJECT_DIR}

cp parameters.yaml parameters.yaml.bak_SCAN

echo "NPoM Volume Scan n=20 — Paper 2 Table 2 recalculation"
echo "Start: $(date -u -Iseconds)"

RESULTS=npom_scan_n20_results.csv
echo "vol_nm3,g0_cm1,phi_FT,elapsed_s,status" > ${RESULTS}

VOLUMES="0.2 0.4 0.6 0.8 1.0 1.2 1.4"

for V in ${VOLUMES}; do
    echo "=== V=${V} nm3 ==="
    START=$(date +%s)

    ${PYTHON} -c "
import yaml
with open('parameters.yaml') as f:
    d = yaml.safe_load(f)
d['quantum']['npom']['enabled'] = True
d['quantum']['fmo']['mode_volume_nm3'] = float('${V}')
d['quantum']['solver']['n_traj'] = 20
d['simulation']['temperature_k'] = 295.0
with open('parameters.yaml', 'w') as f:
    yaml.dump(d, f, default_flow_style=False)
"

    OPENBLAS_NUM_THREADS=1 PYTHONPATH=${PROJECT_DIR}:${FRAMEWORK_DIR} \
        ${PYTHON} main.py \
        --log-file "logs/scan_V${V}_n20.log" \
        > "logs/scan_V${V}_n20_stdout.log" 2>&1
    STATUS=$?

    END=$(date +%s)
    ELAPSED=$((END - START))

    YIELD=$(grep -oP 'Phi_FT.*?\K[0-9.]+' logs/scan_V${V}_n20.log 2>/dev/null || echo "FAILED")
    G0=$(grep -oP 'g0=\K[0-9.]+' logs/scan_V${V}_n20.log 2>/dev/null || echo "0")

    echo "${V},${G0},${YIELD},${ELAPSED},${STATUS}" >> ${RESULTS}
    echo "  -> Phi_FT=${YIELD}, g0=${G0} cm-1 (${ELAPSED}s, status=${STATUS})"
done

cp parameters.yaml.bak_SCAN parameters.yaml

echo "Scan complete. Results in ${RESULTS}"
echo "End: $(date -u -Iseconds)"
