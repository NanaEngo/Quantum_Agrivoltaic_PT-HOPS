# Redac_Paper2 — Espace de travail Paper 2 (Agrivoltaïque quantique)

Répertoire de travail du **Paper 2** : dynamique quantique exacte (PT-HOPS/SBD),
jumeau numérique agrivoltaïque, deux packages de soumission.
Structure mise en place le 2026-09-25, **restructurée et purgée le 2026-09-26**
(suppression des artefacts obsolètes : `reports/`, `_bmad-output/`, `results/`,
bibliographie racine non utilisée, doublons one-shot ; voir historique git).

## Packages de soumission (la seule sortie qui compte)

| Dossier | Journal cible | État (2026-09-26) |
|---|---|---|
| `Submission_Package_AppliedEnergy_Manuscript/` | Applied Energy (Elsevier) | main **45 pp** / SM **26 pp** / cover 1 p — audit **62/62** (local + HPC) |
| `Submission_Package_QST_Manuscript/` | QST (IOP) | main 20 pp / SI 30 pp / cover 2 pp — audit **22/22** (local + HPC) |

Chaque package embarque son `verify_acceptance.py` — **à relancer après toute
retouche**. Checklist d'upload AE : `CHECKLIST_UPLOAD_AppliedEnergy.md` (ORCID
4/5 — Vedekoi à créer ; reviewers vérifiés 4/4 AE et 5/5 QST).

Le package AE est le canon (après déclin du transfert Nature Energy, archivé
dans `_archive/Submission_Package_Nature_Energy_Manuscript/` en haut de repo —
ne jamais resynchroniser son canon financier historique avec l'ère AE).

## Fichiers de la racine

| Fichier | Rôle |
|---|---|
| `main.py` | Orchestrateur (pipeline 10 étapes : dynamique → LCA → écriture HDF5) |
| `Makefile`, `pyproject.toml`, `.pre-commit-config.yaml` | Outillage dev (tests : `make test`) |
| `parameters.yaml` | Config canonique du run (teintes 0.41, seuil 850/750, revenu 30075, Γ_RC commentée en fs⁻¹) |
| `COMPARAISON_Juin_Juillet_QST_AE_260924.md` | Ères de données juin/juillet + comparaison des packages (tenu à jour) |

## Dossiers

| Dossier | Contenu |
|---|---|
| `docs/` | Docs historiques juin/juillet : audit journal 2026-07-29, analyse des données NPoM |
| `scripts/` | Scripts d'exécution (`run_*.sh`, `launch_production.sh`, `run_production_paper2.sh`), extracteur `check_h5_vals.py`, `collect_relaunch_results.sh`, générateurs (`regenerate_figures.py`, `generate_latex_table.py`) |
| `src/` | Code canonique. **Attention** : utiliser `config.lca.cooperative.area_m2` (le `footprint_m2` vintage a causé le crash 7/7 du 20260923) |
| `data/converged/` | HDF5 de production (git-ignoré, sauf `production_dynamics.h5`) ; relances dans `relaunch_<STAMP>/V*/…` |
| `backups/` | `relaunch_20260924/` : **preuve cross-validation n=20 committée** (7 HDF5 + sidecars + verdict + puller `pull_relaunch_h5.sh`) |
| `tests/` | Tests unitaires/intégration — **128 passed / 1 xfailed** (env `fl_qom`) |
| `Submission_Package_AppliedEnergy_Manuscript/plot_si_figures.py` | Régénère les Fig. S1/S2 du SI depuis `data/converged/*.h5` |
| `Submission_Package_AppliedEnergy_Manuscript/plot_plateau_canopy.py` | Régénère la Fig. 1 (plateau canopée) |

## Canon numérique (2026-09-23, validé par HDF5 le 2026-09-24 ; économie audité 2026-09-26)

**Φ_FT = Γ_RC · ∫(P₃+P₄) dt — SANS préfacteur 2** (le bug ×2 de l'ère juillet
stockait `rc_yield = 2·Φ_FT` ; toute valeur stockée > 1 est non physique).

Scan volume 7 points (n=20, tolérance ±0.002 vs canon, V0.8/V1.2 exacts) :

| V (nm³) | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 | 1.2 | 1.4 |
|---|---|---|---|---|---|---|---|
| Φ_FT | 0.0505 | 0.0605 | 0.0727 | 0.0768* | 0.0793 | **0.0799** | 0.0791 |

\* 0.0768 = référence n=100. Max à V=1.2 (−91.8 % vs baseline passive 0.980,
cap modèle et non intégrale de trajectoire) ; φ_global = 0.971 à α = 0.01
(coût d'intégration NPoM : 0.9 point).

Chaîne économique (canon AE, tout recoupé par code + Monte-Carlo 10⁵ grain 42) :
eau **460 L/m²/yr** (230 m³) · ET 4.505/3.246 mm/j (−28 %) · NEB
**72.6**/84.2/0 kg CO₂e/m²/yr · revenu **30 075 USD** · cashflow 26 075 ·
CAPEX 322 USD/m² (subvention 30 % → 112 700) · payback **4.32** (6.17 non
subventionné, 2.68 matériaux locaux) · NPV₁₀@12 % **+34 630 USD** ·
LCOE ≈ 0.36 USD/kWh. Détail : `README_AppliedEnergy.md` + `verify_acceptance.py`
(62 contrôles).

Valeurs validées sur 14 runs indépendants (relances 20260923 + 20260924,
verdict `backups/relaunch_20260924/canon_verdict_20260924.txt`, HDF5 archivés).

## Conventions dures (leçons des incidents)

1. **rsync local↔HPC** : toujours `--checksum` (le mtime ment après copie) ;
   vérifier le **chemin source** avant d'exécuter (incident du 25/09 :
   mauvais cwd → 227 fichiers au mauvais endroit, réparé sans perte).
   Jamais de `--delete` global vers le serveur (exclusivités serveur :
   `backups/ data/ logs/ …`) — purger par liste de chemins explicite.
2. **Purge d'artefacts LaTeX** : `.aux/.log/.out/.bbl/…` oui — mais **le log
   pdflatex de la cover AE est une dépendance d'audit** (contrôle page count) ;
   le préserver, et re-cycler bibtex après chaque purge.
3. **Emails reviewers/ORCID** : jamais de valeur devinée — seulement des
   sources officielles vérifiées (piège de disposition des badges ACS, piège
   de métadonnées AIP legacy documentés dans la checklist).
4. **HPC** : `nanaengo@100.73.21.40`, python `~/miniforge3/envs/MesoHOP-sim/bin/python`,
   projet `~/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2`.
