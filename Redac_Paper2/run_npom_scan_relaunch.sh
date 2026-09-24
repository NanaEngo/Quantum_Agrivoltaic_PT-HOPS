#!/bin/bash
# Relance des scans NPoM volumes avec le code CORRIGE (sans prefacteur 2).
# Canon 2026-09-23 : Phi_FT = Gamma_RC * sum(trapped_pop) * dt  (pas de facteur 2).
# Les 7 volumes tournent EN PARALLELE dans des clones legers de l'arbre principal.
# Resultats : npom_scan_relaunch_<STAMP>.csv + relaunch_<STAMP>/V*/data/converged/*.h5
#
# Historique : la relance 20260923 a complete la PHYSIQUE (Phi_FT au canon 7/7,
# voir V*/scan_vol_*.log) puis a echoue avant la sauvegarde HDF5 sur
# "AttributeError: 'LcaSection' object has no attribute 'footprint_m2'"
# (src d'vintage juillet copie dans les clones). La relance 20260924 utilise
# le src/ local canonique (orchestrator L378 = config.lca.cooperative.area_m2).

set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"

STAMP="20260924"
VOLUMES=(0.2 0.4 0.6 0.8 1.0 1.2 1.4)
PY="$HOME/miniforge3/envs/MesoHOP-sim/bin/python"

for V in "${VOLUMES[@]}"; do
  D="relaunch_${STAMP}/V${V}"
  rm -rf "$D"
  mkdir -p "$D/data/converged" "$D/logs"
  # Base = YAML de PRODUCTION scan_A2 (n_traj=20, T=295K, L=8, dt=0.2 fs,
  # 1000 fs) — protocol des tables publiées ; on ne re-patch que le volume.
  if [ -f scan_A2/parameters.yaml ]; then
    cp scan_A2/parameters.yaml "$D/"
  else
    cp parameters.yaml "$D/"
  fi
  cp main.py "$D/"
  cp -r src "$D/"
  [ -d Graphics ] && cp -r Graphics "$D/"
done

# Le solver resout le framework TROIS niveaux au-dessus de src/quantum_interface/,
# c.-a-d. a la racine du dossier relaunch (comme le framework racine du projet
# utilise par les runs main/scan_A*). Les copies locales etant des squelettes
# sans .py, on symlink le framework reel (racine projet, sinon $HOME).
FW_TARGET="$(pwd)/../quantum_simulations_framework"
[ -f "$FW_TARGET/src/core/hops_simulator.py" ] || FW_TARGET="$HOME/quantum_simulations_framework"
rm -f relaunch_${STAMP}/V*/quantum_simulations_framework
ln -sfn "$FW_TARGET" "relaunch_${STAMP}/quantum_simulations_framework"
echo "Framework -> $(readlink relaunch_${STAMP}/quantum_simulations_framework)"

echo "vol_nm3,phi_FT,elapsed_s,status" > "npom_scan_relaunch_${STAMP}.csv"

for V in "${VOLUMES[@]}"; do
  D="relaunch_${STAMP}/V${V}"
  (
    cd "$D"
    "$PY" -c "
import yaml
with open('parameters.yaml') as f:
    d = yaml.safe_load(f)
d['quantum']['npom']['enabled'] = True
d['quantum']['fmo']['mode_volume_nm3'] = $V
d['quantum']['solver']['n_traj'] = 20
with open('parameters.yaml', 'w') as f:
    yaml.dump(d, f, default_flow_style=False)
"
    export PYTHONPATH="$PWD:$HOME/quantum_simulations_framework"
    export OPENBLAS_NUM_THREADS=1
    nohup "$PY" main.py --log-file "scan_vol_${V}.log" \
        > "scan_vol_${V}_stdout.log" 2>&1 &
    echo "V=${V} lance (pid $!)"
  )
done

echo "7 scans lances en parallele dans relaunch_${STAMP}/V*"
echo "Suivi : tail -f relaunch_${STAMP}/V*/scan_vol_*.log"
