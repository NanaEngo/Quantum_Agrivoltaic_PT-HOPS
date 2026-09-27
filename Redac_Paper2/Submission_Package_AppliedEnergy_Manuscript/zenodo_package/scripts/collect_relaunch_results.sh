#!/bin/bash
# Collecte + verification des resultats de la relance parallele (code corrige,
# sans prefacteur 2). Attend la fin des 7 runs, agrege le CSV et verifie le
# canon 2026-09-23 : Phi_FT = Gamma_RC * int(P3+P4) dt (V=1.2 -> ~0.0799,
# jamais > 1, serie monotone croissante).

set -u
cd "$(cd "$(dirname "$0")" && pwd)"

STAMP="20260924"
BASE="relaunch_${STAMP}"
CSV="npom_scan_relaunch_${STAMP}.csv"
PY="$HOME/miniforge3/envs/MesoHOP-sim/bin/python"
VOLUMES=(0.2 0.4 0.6 0.8 1.0 1.2 1.4)

echo "[$(date '+%F %T')] Collecteur demarre — attente des 7 runs..."

while true; do
  done_count=$(ls ${BASE}/V*/data/converged/*.h5 2>/dev/null | wc -l)
  proc_count=$(pgrep -fc "MesoHOP-sim/bin/python main.py" || true)
  if [ "${done_count}" -ge 7 ]; then
    echo "[$(date '+%F %T')] Les 7 HDF5 sont presents."
    break
  fi
  if [ "${proc_count}" -eq 0 ]; then
    echo "[$(date '+%F %T')] Plus aucun processus main.py (HDF5: ${done_count}/7) — passage a la collecte partielle."
    break
  fi
  echo "[$(date '+%F %T')] HDF5: ${done_count}/7, processus: ${proc_count} — nouvelle verification dans 5 min."
  sleep 300
done

echo "vol_nm3,phi_FT,elapsed_s,status" > "$CSV"

for V in "${VOLUMES[@]}"; do
  D="${BASE}/V${V}"
  LOG="$D/scan_vol_${V}.log"
  if [ -f "$LOG" ]; then
    START=$(head -1 "$LOG" | grep -oP '^\d{2}:\d{2}:\d{2}' | head -1)
  fi
  H5=$(ls "$D"/data/converged/*.h5 2>/dev/null | head -1)
  if [ -z "$H5" ]; then
    # Fallback : extraire Phi_FT depuis le log de run (etape [6/10]) si le
    # HDF5 manque (crash tardif) — la physique est complete avant [10/10].
    PHI=$(grep -oP 'Reaction center trapping yield \(Phi_FT\): \K\d+\.\d+' "$LOG" 2>/dev/null | tail -1)
    if [ -n "$PHI" ]; then
      SUMTP="log-only (pas de HDF5)"; STATUS="ok_log"
    fi
  fi
  if [ -n "$H5" ]; then
    LINE=$("$PY" - "$H5" <<'PYEOF'
import h5py, sys
with h5py.File(sys.argv[1], "r") as f:
    ry = float(f["dynamics/rc_yield"][-1])
    tp = float(f["dynamics/trapped_pop"].sum())
print(f"{ry:.4f},{tp:.3f}")
PYEOF
)
    PHI=$(echo "$LINE" | cut -d, -f1)
    SUMTP=$(echo "$LINE" | cut -d, -f2)
    STATUS="ok"
  else
    PHI="NA"; SUMTP="NA"; STATUS="FAILED"
  fi
  echo "$V,${PHI},NA,${STATUS}" >> "$CSV"
  echo "V=${V}: phi_FT=${PHI} (sum trapped_pop=${SUMTP}, status=${STATUS})"
done

echo ""
echo "=== VERIFICATION CANON (sans prefacteur 2) ==="
"$PY" - "$CSV" <<'PYEOF'
import csv, sys

rows = {r["vol_nm3"]: r["phi_FT"] for r in csv.DictReader(open(sys.argv[1]))}
canon = {"0.2": 0.0505, "0.4": 0.0605, "0.6": 0.0727, "0.8": 0.0761,
         "1.0": None, "1.2": 0.0799, "1.4": None}
ok = True
vals = []
for v in ["0.2", "0.4", "0.6", "0.8", "1.0", "1.2", "1.4"]:
    raw = rows.get(v, "NA")
    if raw == "NA":
        print(f"V={v}: ABSENT"); ok = False; continue
    x = float(raw)
    vals.append((v, x))
    if x > 1.0:
        print(f"V={v}: {x:.4f} > 1 — NON PHYSIQUE (facteur 2 non corrige ?)"); ok = False
    ref = canon[v]
    if ref is not None and abs(x - ref) > 0.002:
        print(f"V={v}: {x:.4f} vs canon {ref:.4f} — ECART {x-ref:+.4f}"); ok = False
    elif ref is not None:
        print(f"V={v}: {x:.4f} vs canon {ref:.4f} — OK")
xs = [x for _, x in vals]
if all(xs[i] <= xs[i+1] + 1e-9 for i in range(len(xs)-1)):
    print("Monotonie croissante : OK")
else:
    print("Monotonie croissante : VIOLEE"); ok = False
print("\nVERDICT :", "CANON VALIDE — tous les rc_yield sont au canon sans facteur 2" if ok else "ECARTS DETECTES — voir ci-dessus")
PYEOF

echo ""
echo "CSV final : $(pwd)/$CSV"
cat "$CSV"
