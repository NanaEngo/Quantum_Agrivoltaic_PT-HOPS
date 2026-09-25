# Redac_Paper2 — Espace de travail Paper 2 (Agrivoltaïque quantique)

Répertoire de travail du **Paper 2** : dynamique quantique exacte (PT-HOPS/SBD),
jumeau numérique agrivoltaïque, deux packages de soumission.
Ce README documente la structure mise en place le 2026-09-25 (racine rangée :
11 fichiers canoniques, tout le reste classé).

## Packages de soumission (la seule sortie qui compte)

| Dossier | Journal cible | État (2026-09-25) |
|---|---|---|
| `Submission_Package_AppliedEnergy_Manuscript/` | Applied Energy (Elsevier) | main 38 pp / SM 24 pp / cover 1 p — audit **62/62** (local + HPC) |
| `Submission_Package_QST_Manuscript/` | QST (IOP) | main 20 pp / SI 30 pp / cover 2 pp — audit **22/22** (local + HPC) |

Chaque package embarque son `verify_acceptance.py` — **à relancer après toute
retouche**. Checklist d'upload AE : `CHECKLIST_UPLOAD_AppliedEnergy.md` (ORCID
4/5 — Vedekoi à créer ; reviewers vérifiés 4/4 AE et 5/5 QST).

## Fichiers de la racine

| Fichier | Rôle |
|---|---|
| `main.py` | Orchestrateur (pipeline 10 étapes : dynamique → LCA → écriture HDF5) |
| `Makefile`, `pyproject.toml`, `.pre-commit-config.yaml` | Outillage dev (tests : `make test`) |
| `parameters.yaml` | Config canonique du run (le symlink `quantum_simulations_framework` est **référencé par le code** — ne pas supprimer) |
| `references.bib` | Biblio partagée des deux packages |
| `COMPARAISON_Juin_Juillet_QST_AE_260924.md` | Ères de données + comparaison des packages (tenu à jour) |
| `npom_scan_relaunch_20260923.csv`, `npom_scan_relaunch_20260924.csv` | Sorties des collecteurs de relance (phi_FT vides côté CSV — les sidecars `.vals` sont la source de vérité) |

## Dossiers

| Dossier | Contenu |
|---|---|
| `docs/` | Docs historiques juin/juillet : audits adversariaux, revues, synthèses |
| `scripts/` | Tous les scripts d'exécution (`run_*.sh`, `launch_production.sh`), sbatch SLURM, `check_h5_vals.py` (extracteur h5py), `collect_relaunch_results.sh`, fixers one-shot |
| `src/` | Code canonique. **Attention** : utiliser `config.lca.cooperative.area_m2` (le `footprint_m2` vintage a causé le crash 7/7 du 20260923) |
| `data/converged/` | HDF5 de production (git-ignoré) ; relances dans `relaunch_<STAMP>/V*/…` |
| `backups/` | `relaunch_20260924/` : **preuve cross-validation n=20 committée** (7 HDF5 + sidecars + verdict) ; `config_july2026/` : snapshots parameters.yaml |
| `results/` | Sorties d'analyse ; `npom_scan_legacy_july2026/` : CSV ère juillet (bug ×2) |
| `logs/`, `reports/`, `tests/`, `Graphics/`, `_bmad-output/` | Logs, rapports, tests unitaires (118 pass), figures legacy, artefacts d'orchestration |
| `relaunch_20260923/`, `relaunch_20260924/` | Runs des relances (logs `scan_vol_*.log`, `data/converged/`) |

## Canon numérique (2026-09-23, validé par HDF5 le 2026-09-24)

**Φ_FT = Γ_RC · ∫(P₃+P₄) dt — SANS préfacteur 2** (le bug ×2 de l'ère juillet
stockait `rc_yield = 2·Φ_FT` ; toute valeur stockée > 1 est non physique).

Scan volume 7 points (n=20, tolérance ±0.002 vs canon, V0.8/V1.2 exacts) :

| V (nm³) | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 | 1.2 | 1.4 |
|---|---|---|---|---|---|---|---|
| Φ_FT | 0.0505 | 0.0605 | 0.0727 | 0.0768* | 0.0793 | **0.0799** | 0.0791 |

\* 0.0768 = référence n=100. Max à V=1.2 (−91.8 % vs baseline passive 0.980) ;
φ_global = 0.971 à α = 0.01 (coût d'intégration NPoM : 0.9 point).

Valeurs validées sur 14 runs indépendants (relances 20260923 + 20260924,
verdict `canon_verdict_20260924.txt`, HDF5 archivés).

## Conventions dures (leçons des incidents)

1. **rsync local↔HPC** : toujours `--checksum` (le mtime ment après copie) ;
   vérifier le **chemin source** avant d'exécuter (incident du 25/09 :
   mauvais cwd → 227 fichiers au mauvais endroit, réparé sans perte).
2. **Purge d'artefacts LaTeX** : `.aux/.log/.out/.bbl/…` oui — mais **le log
   pdflatex de la cover AE est une dépendance d'audit** (contrôle page count) ;
   le préserver, et re-cycler bibtex après chaque purge.
3. **Emails reviewers/ORCID** : jamais de valeur devinée — seulement des
   sources officielles vérifiées (piège de disposition des badges ACS, piège
   de métadonnées AIP legacy documentés dans la checklist).
4. **HPC** : `nanaengo@100.73.21.40`, python `~/miniforge3/envs/MesoHOP-sim/bin/python`,
   projet `~/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2`.
