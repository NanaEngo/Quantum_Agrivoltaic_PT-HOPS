# Synthèse Projet 2 — Quantum Agrivoltaics (Nature Energy)

**Date de synthèse :** 2026-06-22  
**Dossier :** `Redac_Paper2/`  
**Cible :** *Nature Energy* (Research Article, subscription route sans APC)

---

## 1. État Général

| Domaine | Statut | Détails |
|---------|--------|---------|
| Code source | **16/16 tests OK** ✅ | 21 fichiers, ~1 666 lignes Python |
| Manuscrit principal | **Compile (12pp)** ✅ | `Nature_Energy/Manuscript.tex` |
| Supporting Information | **Compile** ✅ | `Nature_Energy/SI.tex` |
| Simulation framework | **Intégré** ✅ | Dépend de `quantum_simulations_framework/` |
| Pre-commit hooks | **Installé** ✅ | Ruff check + format |
| Lint (Ruff) | **Zéro erreur** ✅ | E,W,F,I,C,B |

---

## 2. Architecture du Code

```
Redac_Paper2/
├── main.py                          # Point d'entrée CLI
├── parameters.yaml                  # Configuration unique (60+ clés)
├── src/
│   ├── constants.py                 # 55+ constantes physiques
│   ├── config_loader.py             # Modèles Pydantic validés
│   ├── orchestrator.py              # Pipeline global d'intégration
│   ├── quantum_interface/           # Dynamique quantique (PT-HOPS/SBD)
│   │   ├── hamiltonian.py           # Hamiltonien FMO 8-sites
│   │   ├── solver.py                # MesoHopsSolver + QuantumStabilityAudit
│   │   ├── pulse.py                 # Floquet Stark + OMIT
│   │   └── diagnostics.py           # Couplage NPoM + SERS
│   ├── microclimate/
│   │   └── fao56.py                 # Évapotranspiration (Penman-Monteith)
│   ├── lca/
│   │   ├── database.py              # Amortissement coopératif
│   │   ├── neb.py                   # Bénéfice écologique net (NEB)
│   │   └── plot_utils.py            # Figures 600 DPI
│   └── iot_security/
│       ├── qkd.py                   # Protocole BB84 QKD
│       └── sensing.py               # Capteurs GQD + stress hydrique
├── tests/unit/                      # 16 tests unitaires
├── Nature_Energy/                   # Version soumission manuscrit
│   ├── Manuscript.tex
│   ├── SI.tex
│   └── Cover_Letter.tex
└── _bmad-output/                    # Artéfacts de planification
```

### 2.1 Flux d'exécution (`orchestrator.py`)

1. Chargement config → `parameters.yaml`
2. Construction Hamiltonien FMO 8 sites (non-hermitien, pièges sites 3,4)
3. Dressing NPoM plasmon → Hamiltonien 9×9
4. Floquet Stark (protection photo-dynamique) + OMIT
5. **MesoHOPS** : Propagation PT-HOPS/SBD (L=8, K=2, dt=0.2 fs, N=2)
6. Audit de stabilité (trace, positivité) → HDF5
7. Diagnostic SERS (spectre Raman in situ)
8. FAO-56 : Évapotranspiration sous serre (vent réduit à 10%)
9. LCA NEB : Scénarios A/B/C, amortissement coopératif
10. Figures : Dynamique quantique, SERS, comparaison NEB

---

## 3. Corrections Effectuées (Session 2026-06-22)

### 3.1 Bug Critique : Stockage adaptatif MesoHOPS
- **Cause** : `trajectory.storage.data["psi_traj"]` court-circuite `__getitem__`
- **Conséquence** : Renvoie données sparse de taille 1 au lieu du vecteur d'état complet (9)
- **Fix** : → `trajectory.storage["psi_traj"]` (déclenche la décompression adaptative)

### 3.2 Bug Import Framework
- **Cause** : `quantum_simulations_framework/src/` sans `__init__.py` (namespace package)
- **Conséquence** : `Redac_Paper2/src/` (package régulier) gagnait le conflit de résolution
- **Fix** : `__init__.py` ajouté → ordre `sys.path` décide

### 3.3 Données Incohérentes
| Problème | Correction |
|----------|-----------|
| `dt=0.5` fs dans manuscrit vs `0.2` fs dans config | Manuscrit → `0.2` fs |
| Vent serre non réduit à 10% dans code | `WIND_SPEED_GREENHOUSE_FACTOR = 0.10` |
| `acknowledgement` (singulier) | → `acknowledgements` (pluriel, standard LaTeX) |
| `\usepackage[version=4]{siunitx}` | → `\usepackage{siunitx}` (compat v3) |
| `\numproduct{9x9}` (obsolète siunitx v3) | → `$9 \times 9$` |
| `\SIlist` (obsolète) | → `\qtylist` |

### 3.4 Qualité de Code
- Constants extraites : `TRACE_UPPER_BOUND`, `POSITIVITY_TOLERANCE`, `MM_TO_LITER_PER_M2`, `WIND_SPEED_GREENHOUSE_FACTOR`, `FAO56_ABSOLUTE_ZERO_C`
- `2.0 * gamma_rc` → `len(TRAPPING_SITES) * gamma_rc` (robuste au changement de nombre de sites)
- `orchestrator.py` : imports relatifs (cohérence avec le reste de `src/`)
- `sys.path` manipulation retirée de `orchestrator.py`
- `ruff format` appliqué

---

## 4. Tests

```
16 passed in 6.95s

test_config.py           ✅  1/1  (chargement config)
test_fao56.py            ✅  5/5  (ET, zéro absolu, humidité, NEB, amortissement)
test_qkd_security.py     ✅  3/3  (capteur GQD, cas limites, BB84)
test_quantum_solver.py   ✅  7/7  (Hamiltonien, couplage, NPoM, Floquet, SERS, audit, MesoHOPS)
```

**Couverture :** 62% globale (0% orchestrator.py, 0% plot_utils.py — pas de tests d'intégration encore)

---

## 5. Manuscrit

| Fichier | Pages | Statut |
|---------|-------|--------|
| `Manuscript_NatureEnergy_26-06-18.tex` | 8 | Draft (quality gates 1 ✅, 2-10 ❌) |
| `Nature_Energy/Manuscript.tex` | 12 | Version propre soumission |
| `Nature_Energy/SI.tex` | ~15 | Supporting Information (8 sections) |
| `Nature_Energy/Cover_Letter.tex` | 2 | Lettre de soumission |

**Problèmes restants :**
- ORCIDs : `0000-0000-0000-0000` (placeholders)
- Section Discussion : citations incomplètes
- Figures 2-3 : intégrées seulement dans `Nature_Energy/`

---

## 6. Production Server

**Accès :** `ssh -i /home/taamangtchu/.ssh/taiscale_key nanaengo@100.73.21.40`  
**Environnement :** `MesoHOP-sim` (Python 3.12, MesoHOPS 1.7.0)  
**Framework :** `~/quantum_simulations_framework/`  
**Code Paper 2 :** `~/Redac_Paper2/`

### Commandes de base
```bash
# Test rapide
PYTHONPATH=/home/nanaengo ~/miniforge3/envs/MesoHOP-sim/bin/python -m pytest ~/Redac_Paper2/tests/unit/ -v

# Production (N=100, L=8)
cd ~ && PYTHONPATH=/home/nanaengo nohup ~/miniforge3/envs/MesoHOP-sim/bin/python ~/Redac_Paper2/main.py \
  --solar-flux 800 --log-file logs/production_run.log > production_run.log 2>&1 &
```

### Paramètres de production
| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| `hierarchy_depth` | 8 | Convergence vérifiée (MAE 3e-11) |
| `time_step_fs` | 0.2 | Convergence temporelle |
| `k_matsubara` | 2 | Convergence Matsubara |
| `n_traj` | 100 | Échantillonnage statistique |
| `sbd_bundles_per_site` | 3 | Compression SBD (C(24,7)=346K états) |
| `simulation_duration_fs` | 1000.0 | Capture plateau rendement |

---

## 7. Prochaines étapes

1. **Lancer production sur serveur** avec script bash d'orchestration complet
2. **Analyser données** : rendement de piégeage, spectres SERS, convergence N_traj
3. **Mettre à jour manuscrit** avec résultats réels (Figures 1-3)
4. **Compléter SI** : tableaux de convergence, paramètres de bain
5. **ORCIDs** : remplacer les placeholders
6. **Intégrer `orchestrator.py`** dans les tests (couverture > 80%)
