#!/usr/bin/env bash
# =============================================================================
# Orchestrateur de Production — Paper 2 (Nature Energy)
# Quantum Agrivoltaics : PT-HOPS/SBD + FAO-56 + LCA + QKD
# =============================================================================
# Usage :
#   bash run_production_paper2.sh              # Production complète
#   bash run_production_paper2.sh --test       # Test rapide (N=2, L=3)
#   bash run_production_paper2.sh --stage 1    # Étape 1 seulement
#   bash run_production_paper2.sh --dry-run    # Affiche les commandes
# =============================================================================

set -euo pipefail

# ---- Configuration ----
PROJECT_DIR="${PROJECT_DIR:-$HOME/Redac_Paper2}"
FRAMEWORK_DIR="${FRAMEWORK_DIR:-$HOME/quantum_simulations_framework}"
CONDA_ENV="${CONDA_ENV:-MesoHOP-sim}"
PYTHON="${PYTHON:-$HOME/miniforge3/envs/${CONDA_ENV}/bin/python}"
PIP="${PIP:-$HOME/miniforge3/envs/${CONDA_ENV}/bin/pip}"
LOG_DIR="${PROJECT_DIR}/logs"
DATA_DIR="${PROJECT_DIR}/data/converged"
GRAPHICS_DIR="${PROJECT_DIR}/Graphics"
REPORT_DIR="${PROJECT_DIR}/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RUN_ID="paper2_prod_${TIMESTAMP}"
LOG_FILE="${LOG_DIR}/${RUN_ID}.log"
ANALYSIS_FILE="${REPORT_DIR}/ANALYSIS_${TIMESTAMP}.md"

mkdir -p "$LOG_DIR" "$DATA_DIR" "$GRAPHICS_DIR" "$REPORT_DIR"

# ---- Paramètres par défaut ----
SOLAR_FLUX=${SOLAR_FLUX:-800}
N_TRAJ=${N_TRAJ:-100}
HIERARCHY_DEPTH=${HIERARCHY_DEPTH:-8}
DT_FS=${DT_FS:-0.2}
DURATION_FS=${DURATION_FS:-1000.0}
TEST_MODE=false
DRY_RUN=false
STAGE_FILTER=""

# ---- Couleurs pour les logs ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()   { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE"; }

# ---- Parsing arguments ----
while [[ $# -gt 0 ]]; do
    case "$1" in
        --test)     TEST_MODE=true; shift ;;
        --dry-run)  DRY_RUN=true; shift ;;
        --stage)    STAGE_FILTER="$2"; shift 2 ;;
        --solar-flux) SOLAR_FLUX="$2"; shift 2 ;;
        --n-traj)   N_TRAJ="$2"; shift 2 ;;
        *)          error "Argument inconnu: $1"; exit 1 ;;
    esac
done

if $TEST_MODE; then
    N_TRAJ=2
    HIERARCHY_DEPTH=3
    DURATION_FS=200.0
    log "${YELLOW}=== MODE TEST : N=2, L=3, 200 fs ===${NC}"
fi

log "${BLUE}============================================${NC}"
log "${BLUE}  Paper 2 Production Run${NC}"
log "${BLUE}  Run ID    : ${RUN_ID}${NC}"
log "${BLUE}  N_traj    : ${N_TRAJ}${NC}"
log "${BLUE}  L         : ${HIERARCHY_DEPTH}${NC}"
log "${BLUE}  dt        : ${DT_FS} fs${NC}"
log "${BLUE}  Duration  : ${DURATION_FS} fs${NC}"
log "${BLUE}  Flux      : ${SOLAR_FLUX} W/m²${NC}"
log "${BLUE}============================================${NC}"

# ---- Fonctions de vérification ----
check_environment() {
    log "[CHECK] Vérification de l'environnement..."
    if ! $DRY_RUN; then
        $PYTHON -c "import numpy, scipy, h5py, matplotlib, yaml, pydantic; print('OK')" 2>/dev/null || {
            error "Dépendances manquantes. Installation..."
            $PIP install numpy scipy h5py matplotlib pyyaml pydantic
        }
        $PYTHON -c "import mesohops; print('MesoHOPS:', mesohops.__file__)" 2>/dev/null || {
            warn "MesoHOPS non trouvé dans l'environnement"
        }
    fi
    log "[CHECK] Environnement OK"
}

check_framework() {
    log "[CHECK] Vérification du framework..."
    if [ ! -d "$FRAMEWORK_DIR" ]; then
        error "Framework non trouvé: $FRAMEWORK_DIR"
        exit 1
    fi
    if $DRY_RUN; then return; fi
    $PYTHON -c "
import sys
sys.path.insert(0, '${FRAMEWORK_DIR}')
from src.core.hops_simulator import HopsSimulator
print('Framework OK')
" 2>&1 | tee -a "$LOG_FILE" || {
        error "Framework import échoué"
        exit 1
    }
    log "[CHECK] Framework OK"
}

run_tests() {
    log "[STAGE 0] Exécution des tests unitaires..."
    if $DRY_RUN; then
        log "  (dry-run) PYTHONPATH=$HOME $PYTHON -m pytest $PROJECT_DIR/tests/unit/ -v"
        return
    fi
    cd "$HOME"
    OPENBLAS_NUM_THREADS=1 PYTHONPATH="$PROJECT_DIR:$FRAMEWORK_DIR" $PYTHON -m pytest "$PROJECT_DIR/tests/unit/" -v --tb=short 2>&1 | tee -a "$LOG_FILE"
    local pytest_exit=${PIPESTATUS[0]}
    if [ $pytest_exit -ne 0 ]; then
        if $TEST_MODE; then
            warn "Tests échoués mais mode test continue"
        else
            error "Tests échoués (code: $pytest_exit). Abandon."
            exit 1
        fi
    fi
    log "[STAGE 0] Tests OK"
}

stage_1_simulation() {
    log "[STAGE 1] Lancement de la simulation quantique + pipeline complet..."
    if $DRY_RUN; then
        log "  (dry-run) OPENBLAS_NUM_THREADS=1 PYTHONPATH=$PROJECT_DIR:$FRAMEWORK_DIR $PYTHON $PROJECT_DIR/main.py --solar-flux $SOLAR_FLUX --log-file ${LOG_DIR}/simulation_${TIMESTAMP}.log"
        return
    fi

    local sim_log="${LOG_DIR}/simulation_${TIMESTAMP}.log"
    OPENBLAS_NUM_THREADS=1 PYTHONPATH="$PROJECT_DIR:$FRAMEWORK_DIR" nohup $PYTHON "$PROJECT_DIR/main.py" \
        --solar-flux "$SOLAR_FLUX" \
        --time-step-fs "$DT_FS" \
        --log-file "$sim_log" \
        > "${LOG_DIR}/simulation_stdout_${TIMESTAMP}.log" 2>&1 &
    local SIM_PID=$!
    echo "$SIM_PID" > "${LOG_DIR}/simulation_${TIMESTAMP}.pid"
    log "[STAGE 1] PID: $SIM_PID"

    # Monitoring loop
    local start_time=$(date +%s)
    local last_check=$start_time
    while kill -0 $SIM_PID 2>/dev/null; do
        local now=$(date +%s)
        local elapsed=$((now - start_time))
        if [ $((now - last_check)) -ge 120 ]; then
            local mem=$(free -h | awk '/^Mem:/ {print $3}')
            local swap=$(free -h | awk '/^Swap:/ {print $3}')
            log "  [PROGRESS] ${elapsed}s écoulés | RAM: ${mem} | SWAP: ${swap}"
            last_check=$now
        fi
        # Vérification OOM toutes les 30s
        if [ $((now - start_time)) -ge 30 ]; then
            if ! kill -0 $SIM_PID 2>/dev/null; then
                break
            fi
        fi
        sleep 30
    done

    wait $SIM_PID 2>/dev/null
    local sim_exit=$?
    if [ $sim_exit -ne 0 ] && ! $TEST_MODE; then
        error "Simulation échouée (code: $sim_exit). Consultez $sim_log"
        tail -50 "$sim_log" >> "$LOG_FILE"
        exit 1
    fi
    log "[STAGE 1] Simulation terminée (exit: $sim_exit)"
}

stage_2_data_analysis() {
    log "[STAGE 2] Analyse des données..."
    if $DRY_RUN; then
        log "  (dry-run) Génération du rapport d'analyse"
        return
    fi

    local h5_file="${DATA_DIR}/production_dynamics.h5"
    if [ ! -f "$h5_file" ]; then
        warn "Fichier HDF5 non trouvé: $h5_file"
        ls -la "$DATA_DIR"/ 2>/dev/null >> "$LOG_FILE"
        return
    fi
    local h5_size=$(stat -c%s "$h5_file" 2>/dev/null || echo 0)
    log "  Taille HDF5: $(numfmt --to=iec $h5_size)"

    cat > "$ANALYSIS_FILE" << EOF
# Analyse de Production — Paper 2 (Nature Energy)

**Run ID :** ${RUN_ID}
**Date :** $(date)
**Paramètres :** N=${N_TRAJ}, L=${HIERARCHY_DEPTH}, dt=${DT_FS} fs, flux=${SOLAR_FLUX} W/m²

## 1. Fichiers de sortie

| Fichier | Statut |
|---------|--------|
| \`${h5_file}\` | $(test -f "$h5_file" && echo "✅ $h5_size bytes" || echo "❌ Non trouvé") |
| \`${GRAPHICS_DIR}/Figure1_Quantum_Dynamics.png\` | $(test -f "${GRAPHICS_DIR}/Figure1_Quantum_Dynamics.png" && echo "✅" || echo "❌") |
| \`${GRAPHICS_DIR}/Figure2_SERS_Readout.png\` | $(test -f "${GRAPHICS_DIR}/Figure2_SERS_Readout.png" && echo "✅" || echo "❌") |
| \`${GRAPHICS_DIR}/Figure3_LCA_NEB_Comparison.png\` | $(test -f "${GRAPHICS_DIR}/Figure3_LCA_NEB_Comparison.png" && echo "✅" || echo "❌") |

## 2. Logs de simulation

\`\`\`
$(tail -100 "${LOG_DIR}/simulation_${TIMESTAMP}.log" 2>/dev/null || echo "Log non disponible")
\`\`\`

## 3. Ressources

- PID : $(cat "${LOG_DIR}/simulation_${TIMESTAMP}.pid" 2>/dev/null || echo "N/A")
- Durée : $(ps -o etime= -p $(cat "${LOG_DIR}/simulation_${TIMESTAMP}.pid" 2>/dev/null) 2>/dev/null || echo "Terminé")

EOF
    log "[STAGE 2] Rapport sauvegardé: $ANALYSIS_FILE"
}

stage_3_verify_figures() {
    log "[STAGE 3] Vérification des figures..."
    if $DRY_RUN; then
        log "  (dry-run) Vérification des fichiers PNG dans $GRAPHICS_DIR"
        return
    fi
    local missing=0
    for fig in "Figure1_Quantum_Dynamics.png" "Figure2_SERS_Readout.png" "Figure3_LCA_NEB_Comparison.png"; do
        if [ -f "${GRAPHICS_DIR}/${fig}" ]; then
            local size=$(stat -c%s "${GRAPHICS_DIR}/${fig}" 2>/dev/null || echo 0)
            log "  ✅ ${fig} ($(numfmt --to=iec $size))"
        else
            warn "  ❌ ${fig} manquant"
            missing=$((missing + 1))
        fi
    done
    if [ $missing -gt 0 ] && ! $TEST_MODE; then
        warn "${missing} figure(s) manquante(s)"
    fi
    log "[STAGE 3] Vérification terminée"
}

stage_4_generate_report() {
    log "[STAGE 4] Génération du rapport final..."
    if $DRY_RUN; then
        log "  (dry-run) Consolidation des rapports"
        return
    fi

    # Générer résumé dans le rapport d'analyse
    cat >> "$ANALYSIS_FILE" << EOF

## 4. Résumé des ressources

$(free -h | head -2)

## 5. Disponibilité des figures générées

| Figure | Chemin |
|--------|--------|
| Dynamique quantique | \`${GRAPHICS_DIR}/Figure1_Quantum_Dynamics.png\` |
| SERS Readout | \`${GRAPHICS_DIR}/Figure2_SERS_Readout.png\` |
| LCA NEB | \`${GRAPHICS_DIR}/Figure3_LCA_NEB_Comparison.png\` |

EOF
    log "[STAGE 4] Rapport final: $ANALYSIS_FILE"
}

stage_5_cleanup() {
    log "[STAGE 5] Nettoyage..."
    if $DRY_RUN; then return; fi
    # Nettoyer les fichiers temporaires
    find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$FRAMEWORK_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    log "[STAGE 5] Nettoyage terminé"
}

# ---- Pipeline principal ----
check_environment
check_framework
run_tests
stage_1_simulation
stage_2_data_analysis
stage_3_verify_figures
stage_4_generate_report
stage_5_cleanup

# ---- Résumé final ----
log "${GREEN}============================================${NC}"
log "${GREEN}  Production Paper 2 TERMINÉE${NC}"
log "${GREEN}  Run ID : ${RUN_ID}${NC}"
log "${GREEN}  Log    : ${LOG_FILE}${NC}"
log "${GREEN}  Report : ${ANALYSIS_FILE}${NC}"
log "${GREEN}============================================${NC}"

# Afficher le résumé
cat "$ANALYSIS_FILE" 2>/dev/null | head -30
