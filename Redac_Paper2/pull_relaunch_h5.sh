#!/bin/bash
# Pull automatique des HDF5 de la relance 20260924 (HPC -> local). Version 4.
# - UN seul SSH d'inventaire par cycle (toutes les 10 min) : par volume, taille
#   du HDF5 + nb de processus de run (ps|grep|grep -v grep — fiable) + Phi_FT
#   du log de run si deja present.
# - Pull d'un HDF5 des que le process du volume est termine ; fallback : HDF5
#   froid (taille stable entre deux cycles). Si le process est termine sans
#   HDF5 (crash), double-verification par ls distant puis marque <V>.missing.
#   Destination : data/converged/relaunch_20260924/V*/production_dynamics.h5
# - Sidecar *.vals : grandeurs canoniques (check_h5_vals.py h5py cote HPC) +
#   Phi_FT du log de run ([6/10]).
# - Des que 7 HDF5 (ou missing) + 7 vals : verdict canon (±0.002 vs canon,
#   jamais > 1, monotonie, coherence h5 vs log <= 0.001) ecrit dans
#   canon_verdict_20260924.txt ; arret.
# Canon 2026-09-23 : Phi_FT = Gamma_RC * sum(trapped_pop) * dt, SANS prefacteur 2.
# NB : les ssh internes au while read sont proteges par </dev/null pour ne pas
#      consommer le stdin de la boucle.

set -u
cd "$(cd "$(dirname "$0")" && pwd)"

STAMP="20260924"
BASE="relaunch_${STAMP}"
HPC="nanaengo@100.73.21.40"
HPC_DIR="Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2/${BASE}"
DEST="data/converged/${BASE}"
LOG="pull_${BASE}.log"
DONE="pull_${BASE}.done"
SSH_OPTS="-o BatchMode=yes -o ConnectTimeout=15"
VOLS="0.2 0.4 0.6 0.8 1.0 1.2 1.4"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# --once : un seul cycle puis sortie (pour cron / test) ; defaut : boucle 10 min.
ONCE=0
[ "${1:-}" = "--once" ] && ONCE=1

[ -d "$DEST" ] || mkdir -p "$DEST"
if [ -f "$DONE" ]; then
  log "Deja complet ($DONE present) — rien a faire."
  exit 0
fi
log "Puller v4 demarre — dest: $DEST"

h5path() { printf '%s/V%s/data/converged/production_dynamics.h5' "$HPC_DIR" "$1"; }

# Inventaire distant : "V|taille|nprocs|phi_log" par volume.
# Le heredoc quoté est transmis tel quel au shell distant (pas d'echappement
# double-niveau) ; REMOTE_DIR / VOL_LIST sont substitues avant envoi.
inventory() {
  local REMOTE
  REMOTE=$(cat <<'EOF'
cd REMOTE_DIR 2>/dev/null || exit 9
for v in VOL_LIST; do
  sz=$(stat -c %s "V${v}/data/converged/production_dynamics.h5" 2>/dev/null || echo NA)
  p=$(ps -eo args | grep "scan_vol_${v}.log" | grep -v grep | wc -l)
  phi=$(grep -oP 'Reaction center trapping yield .Phi_FT.: \K[0-9.]+' "V${v}/scan_vol_${v}.log" 2>/dev/null | tail -1)
  echo "${v}|${sz}|${p}|${phi:-na}"
done
EOF
)
  REMOTE=${REMOTE//REMOTE_DIR/$HPC_DIR}
  REMOTE=${REMOTE//VOL_LIST/$VOLS}
  timeout 40 ssh $SSH_OPTS "$HPC" "$REMOTE" 2>/dev/null
}

while :; do
  INV=$(inventory)
  if [ -z "$INV" ]; then
    log "SSH inventaire vide/timeout — nouvel essai dans 10 min."
    sleep 600; continue
  fi

  # --- Pull : process termine => HDF5 fige ; sinon froid ; sinon missing ----
  while IFS='|' read -r V SZ P PHI; do
    case "$V" in ''|---) continue ;; esac
    H5L="$DEST/V${V}/production_dynamics.h5"
    [ -n "$PHI" ] && [ "$PHI" != "na" ] && printf '%s' "$PHI" > "$DEST/V${V}.phi"
    if [ -f "$H5L" ] || [ -f "$DEST/V${V}.missing" ]; then continue; fi
    if [ "$SZ" != "NA" ]; then
      PULL=0; WHY=""
      if [ "$P" = "0" ]; then
        PULL=1; WHY="process termine"
      else
        SZL=$(cat "$DEST/V${V}.size" 2>/dev/null || echo -1)
        echo "$SZ" > "$DEST/V${V}.size"
        if [ "$SZ" = "$SZL" ]; then PULL=1; WHY="froid (${SZ} o)"; fi
      fi
      if [ "$PULL" = "1" ]; then
        log "V${V}: $WHY — pull."
        mkdir -p "$DEST/V${V}"
        if timeout 120 scp -q $SSH_OPTS "$HPC:$(h5path "$V")" "$H5L" </dev/null; then
          log "V${V}: HDF5 rapatrie."
        else
          rm -f "$H5L"; log "V${V}: ECHEC du scp — reessai au prochain cycle."
        fi
      fi
    else
      # Pas de HDF5 : si aucun process et confirme par ls distant => missing.
      if [ "$P" = "0" ]; then
        LSOUT=$(timeout 20 ssh -n $SSH_OPTS "$HPC" "ls $(h5path "$V") 2>/dev/null" || true)
        if [ -z "$LSOUT" ]; then
          touch "$DEST/V${V}.missing"
          log "V${V}: process termine SANS HDF5 (crash ?) — marque missing."
        fi
      fi
    fi
  done <<< "$INV"

  # --- Sidecar vals pour chaque HDF5 present -------------------------------
  for V in $VOLS; do
    [ -f "$DEST/V${V}/production_dynamics.h5" ] || continue
    [ -f "$DEST/V${V}.vals" ] && continue
    VALS=$(timeout 40 ssh -n $SSH_OPTS "$HPC" \
      "cd $HPC_DIR/V${V}/data/converged && \$HOME/miniforge3/envs/MesoHOP-sim/bin/python ../../../../check_h5_vals.py production_dynamics.h5" 2>/dev/null || true)
    if printf '%s' "$VALS" | grep -q '^rc_yield='; then
      PHIL=$(cat "$DEST/V${V}.phi" 2>/dev/null || echo na)
      printf '%s|phi_ft_log=%s\n' "$VALS" "${PHIL:-na}" > "$DEST/V${V}.vals"
      log "V${V}: ${VALS} | phi_ft_log=${PHIL:-na}"
    fi
  done

  # --- Complétion : verdict canon + arret -----------------------------------
  N=$(ls "$DEST"/V*/production_dynamics.h5 2>/dev/null | wc -l | tr -d ' ')
  NM=$(ls "$DEST"/V*.missing 2>/dev/null | wc -l | tr -d ' ')
  NV=$(ls "$DEST"/V*.vals 2>/dev/null | wc -l | tr -d ' ')
  log "Etat : ${N}/7 HDF5, ${NM} missing, ${NV}/7 vals."
  if [ "$((N + NM))" -ge 7 ] && [ "$NV" -ge "$N" ]; then
    VERDICT="canon_verdict_${STAMP}.txt"
    printf 'vol_nm3,rc_yield_h5,phi_ft_log_run,sum_trapped_pop,n_frames\n' > "$VERDICT"
    ok=1; prev=""
    for V in $VOLS; do
      if [ -f "$DEST/V${V}.vals" ]; then VALS=$(cat "$DEST/V${V}.vals"); else VALS=""; fi
      RY=$(printf '%s' "$VALS" | sed -n 's/.*rc_yield=\([0-9.]*\),.*/\1/p')
      SUMTP=$(printf '%s' "$VALS" | sed -n 's/.*,sum_trapped_pop=\([0-9.]*\),.*/\1/p')
      NF=$(printf '%s' "$VALS" | sed -n 's/.*,n_frames=\([0-9]*\),.*/\1/p')
      PHIL=$(printf '%s' "$VALS" | sed -n 's/.*phi_ft_log=\([0-9.]*\).*/\1/p')
      case "$V" in
        0.2) CANON=0.0505 ;; 0.4) CANON=0.0605 ;; 0.6) CANON=0.0727 ;;
        0.8) CANON=0.0761 ;; 1.2) CANON=0.0799 ;; *) CANON="" ;;
      esac
      printf '%s,%s,%s,%s,%s\n' "$V" "${RY:-NA}" "${PHIL:-na}" "${SUMTP:-NA}" "${NF:-NA}" >> "$VERDICT"
      if [ -z "$RY" ]; then
        log "V${V}: PAS DE HDF5 (missing) — verdict sur ce volume impossible."; ok=0; continue
      fi
      if awk -v a="$RY" 'BEGIN{exit !(a>1.0)}'; then
        log "V${V}: ${RY} > 1 NON PHYSIQUE"; ok=0
      fi
      if [ -n "$CANON" ]; then
        d=$(awk -v a="$RY" -v b="$CANON" 'BEGIN{printf "%+.4f", a-b}')
        ad=$(awk -v a="$RY" -v b="$CANON" 'BEGIN{d=a-b; print (d<0)?-d:d}')
        if awk -v x="$ad" 'BEGIN{exit !(x>0.002)}'; then
          log "V${V}: ${RY} vs canon ${CANON} — ECART ${d}"; ok=0
        else
          log "V${V}: ${RY} vs canon ${CANON} — OK (ecart ${d})"
        fi
      fi
      if [ -n "$PHIL" ] && [ "$PHIL" != "na" ]; then
        dh=$(awk -v a="$RY" -v b="$PHIL" 'BEGIN{d=a-b; print (d<0)?-d:d}')
        if awk -v x="$dh" 'BEGIN{exit !(x>0.001)}'; then
          log "V${V}: incoherence h5 (${RY}) vs log run (${PHIL})"; ok=0
        fi
      fi
      if [ -n "$prev" ]; then
        if awk -v a="$prev" -v b="$RY" 'BEGIN{exit !(a>b+1e-9)}'; then
          log "V${V}: monotonie VIOLEE (${prev} > ${RY})"; ok=0
        fi
      fi
      prev="$RY"
    done
    if [ "$ok" = "1" ]; then
      log "VERDICT : CANON VALIDE (7/7, sans facteur 2) — $VERDICT"
    else
      log "VERDICT : ECARTS DETECTES — $VERDICT"
    fi
    cat "$VERDICT" >> "$LOG"
    touch "$DONE"
    exit 0
  fi

  if [ "$ONCE" = "1" ]; then
    log "Mode --once : cycle termine."
    exit 0
  fi
  sleep 600
done
