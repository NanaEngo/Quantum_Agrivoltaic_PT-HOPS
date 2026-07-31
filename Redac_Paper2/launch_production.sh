#!/usr/bin/env bash
# Launch script for Paper 2 production pipeline on server
set -euo pipefail

echo "=== Cleaning up previous runs ==="
pkill -9 -f "main.py" 2>/dev/null || true
pkill -9 -f "run_production" 2>/dev/null || true
sleep 2

rm -f ~/Redac_Paper2/logs/pipeline_*.log
rm -f ~/Redac_Paper2/logs/simulation_*.{log,pid}
rm -f ~/Redac_Paper2/logs/production_*.log
rm -f ~/Redac_Paper2/logs/paper2_*.log

echo "=== Launching production pipeline ==="
cd ~
nohup bash ~/Redac_Paper2/run_production_paper2.sh > ~/Redac_Paper2/logs/pipeline_nohup.log 2>&1 &
echo "LAUNCHED_PID=$!"
echo "=== Launch complete ==="
