#!/bin/bash
#SBATCH --job-name=npom_scan_A2
#SBATCH --output=/home/nanaengo/Redac_Paper2/logs/npom_scan_A2_%j.log
#SBATCH --error=/home/nanaengo/Redac_Paper2/logs/npom_scan_A2_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail
export PYTHONUNBUFFERED=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export XLA_FLAGS=--xla_cpu_multi_thread_eager=false

WORKDIR=/home/nanaengo/Redac_Paper2/scan_A2
PYTHON=/home/nanaengo/miniforge3/envs/MesoHOP-sim/bin/python
cd $WORKDIR
export PYTHONPATH=$WORKDIR:$HOME/quantum_simulations_framework

echo 'NPoM Scan A2 — V=0.6 ONLY (n=20, L=8)'
echo "Start: $(date -u -Iseconds)"

V=0.6
echo "=== V=$V nm3 ==="
$PYTHON -c "
import yaml
with open('parameters.yaml') as f:
    d = yaml.safe_load(f)
d['quantum']['npom']['enabled'] = True
d['quantum']['fmo']['mode_volume_nm3'] = $V
with open('parameters.yaml', 'w') as f:
    yaml.dump(d, f, default_flow_style=False)
"
$PYTHON main.py --log-file "logs/scan_vol_${V}.log" 2>&1 | tail -5
echo "  V=$V done"

echo 'Scan A2 complete'
echo "End: $(date -u -Iseconds)"
