# Plan — Restructurer `Redac_Paper2/`, supprimer les obsolètes, mettre à jour les MD

**Date :** 2026-09-26 · Mode : exécution après approbation · Arbitrage utilisateur : suppressions via `git rm` (récupérables depuis l'historique) ; validation finale = commit + push + rsync HPC.

## 0. Constat (vérifié par exploration)

- `README.md` de `Redac_Paper2/` très périmé : référence 7 artefacts **inexistants** (`npom_scan_relaunch_*.csv`, symlink `quantum_simulations_framework`, `relaunch_20260923/`, `relaunch_20260924/`, `logs/`, `Graphics/`, `backups/config_july2026/`, `results/npom_scan_legacy_july2026/`), pages AE 38/24 (réel 45/26), « tests 118 » (réel 128), « references.bib partagé » (les 2 packages ont leur propre biblio — la racine est **non utilisée**).
- 30 fichiers obsolètes/doublons identifiés (détail §1), dont 15 artefacts BMAD mai-juin redondants avec le `_bmad-output/` racine du repo, et 6 rapports d'audit juin dont le `MASTER_AUDIT_PROMPT.md` pointe vers le package NE archivé.
- Dépendances d'audit à préserver : QST `verify_acceptance.py` exige (a) `AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md` **dans** le package QST (check #5) et (b) l'exemplaire `_archive/Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex` (check #12). AE `verify_acceptance.py` exige `figures/Graphical_Abstract_wide.png` + le log de la cover AE (convention 2 du README).
- Aucune modification `.tex`/PDF n'est prévue → pas de recompilation.

## 1. Suppressions (`git rm` / déplacements)

### 1.1 Racine `Redac_Paper2/`
| Cible | Motif |
|---|---|
| `reports/` (6 MD juin) | Demande explicite `git rm`. Audits/analyses juin supersédés par les tours AE (MAE 62/62). `MASTER_AUDIT_PROMPT.md` pointe vers NE archivé. |
| `_bmad-output/` (15 fichiers) | Demande explicite `git rm`. Artefacts planning mai-juin, redondants avec `_bmad-output/` racine. |
| `results/plot_local_dynamics.py` (+ dir vidé) | Script mort : référence `V*_data.h5` inexistants ; supersédé par `plot_si_figures.py`. |
| `references.bib` racine (152 entrées) | Aucun consommateur : `\bibliography{references}` est résolu localement dans chaque package (AE 193 entrées, QST 177). |
| `pull_relaunch_20260924.done` (0 B) | Marqueur cron terminé (déjà consigné dans le plan d'implémentation § « Clôture outillage »). |
| `canon_verdict_20260924.txt` (racine) | Doublon **byte-identique** de `backups/relaunch_20260924/canon_verdict_20260924.txt` (preuve committée). |

**Déplacement (provenance conservée) :** `pull_relaunch_h5.sh` → `backups/relaunch_20260924/pull_relaunch_h5.sh` (son log est déjà là ; le script est le « puller v4 » documenté au plan d'implémentation).

### 1.2 Package AE (`Submission_Package_AppliedEnergy_Manuscript/`)
| Cible | Motif |
|---|---|
| `fix_percentages.py` | One-shot regex ciblant `Manuscript_NatureEnergy_26-06-25.tex`/`SI.tex` (archivés). |
| `figures/Figure_Comparative_{77K_vs_295K, NPoM_ON_vs_OFF, V08_vs_V12}{,_HD}.png` (6) | Aucun `\includegraphics` ne les référence. |
| `figures/Figure_SI_Comparative_4Runs_HD.png` | Variante HD non référencée (le tex utilise la version non-HD). |
| `figures/Graphical_Abstract.png`, `Graphical_Abstract_fixed.png` | Sources carrées ; seul `_wide.png` est le fichier d'upload (vérification d'audit + README). |

### 1.3 Package QST (`Submission_Package_QST_Manuscript/`)
| Cible | Motif |
|---|---|
| `Manuscript_NatureEnergy_26-06-25.tex` + `.pdf` | Copie héritée NE ; l'exemplaire canonique est dans `_archive/` (contrôlé par le check #12 du verify). |
| `Cover_Letter.tex` + `Cover_Letter.pdf` | Cover ère NE ; le vrai document est `Cover_Letter_QST.tex/.pdf` (seul contrôlé par le verify). |
| `fix_percentages.py` | Idem 1.2. |

**Non touché (délibéré) :** `AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md` (check #5) · `data/converged/*.h5` · `backups/` (preuve n=20 committée) · scripts `run_*.sh`, `collect_*`, `check_h5_vals.py` (traçabilité des runs) · `COMPARAISON_Juin_Juillet_QST_AE_260924.md` (doc vivante) · `plot_volume_scan_light.py` / `plot_coupling_regime.py` (figures SI QST) · `_archive/`, `.claude/` (non tracktés, hors périmètre).

**Nettoyage facultatif (untracked) :** purger les artefacts LaTeX ignorés (`.aux/.bbl/.blg/.out/.toc/.fls/.fdb_latexmk/.spl`) des deux packages **en conservant** le log de la cover AE (dépendance d'audit page-count) et tous les PDF tracktés.

## 2. Arbre cible

```
Redac_Paper2/
├── README.md                      ← réécrit (§3.1)
├── main.py · Makefile · pyproject.toml · parameters.yaml · .gitignore · .pre-commit-config.yaml
├── COMPARAISON_Juin_Juillet_QST_AE_260924.md   ← mis à jour (§3.7)
├── Submission_Package_AppliedEnergy_Manuscript/   ← canonique (62/62)
├── Submission_Package_QST_Manuscript/            ← alternatif Q1 (22/22)
├── src/ · tests/ · scripts/                       ← inchangés
├── data/converged/                 (ignoré sauf production_dynamics.h5)
├── backups/relaunch_20260924/      (+ pull_relaunch_h5.sh déplacé ici)
└── docs/                           ← historique juin/juillet (2 MD, inchangés)
[SUPPRIMÉ : reports/ · _bmad-output/ · results/ · references.bib · marqueurs one-shot]
```

## 3. Mise à jour des fichiers MD

1. **`Redac_Paper2/README.md` (réécriture ciblée)**
   - Table packages : AE « main 45 pp / SM 26 pp / cover 1 p — audit 62/62 (local + HPC) » ; QST « 20/30/2 pp — 22/22 ».
   - Table racine : retirer les lignes CSV/symlink/`references.bib` (« partagée » → supprimée, chaque package possède la sienne) ; conserver `main.py`, outillage, `parameters.yaml` (sans la phrase symlink fausse), `COMPARAISON`.
   - Table dossiers : retirer `reports/`, `_bmad-output/`, `results/`, `relaunch_*`, `logs/`, `Graphics/` ; `docs/` = historique ; ajouter la ligne outils figures (`plot_si_figures.py`, `plot_plateau_canopy.py` dans le package AE).
   - Canon : conserver le canon Φ (bug ×2), ajouter la ligne économique (eau 460 L/230 m³, NEB 72.6/84.2/0, revenu 30 075, cashflow 26 075, payback 4.32/6.17/2.68, NPV +34 630, MC [IC 95 %] de la version AE) + pointeur `README_AppliedEnergy.md`.
   - Conventions dures (rsync `--checksum`, purge LaTeX avec exception log cover, emails/ORCID, HPC) : **conservées telles quelles**.
   - `tests 118` → `128 passed / 1 xfailed` ; mention de la note de restructuration 2026-09-26.
   - Référence `canon_verdict_20260924.txt` → chemin `backups/relaunch_20260924/…`.
2. **`README_AppliedEnergy.md`** : « 39 pp » → **45 pp**, « 25 pp » → **26 pp** ; paragraphe Graphical Abstract : les sources carrées sont supprimées → ne garder que `_wide.png` (2048×1024).
3. **QST `README.md`** : retirer la ligne `Manuscript_NatureEnergy_26-06-25.tex/.pdf` (« inherited base, reference only ») et ajouter « exemplaire archivé : `_archive/Submission_Package_Nature_Energy_Manuscript/` ».
4. **`QST/AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md` L11–12** : les 2 liens `file://…/Redac_Paper2/Pistes_Improvements260625.md` et `…/MASTER_AUDIT_PROMPT.md` deviennent des références « supprimé le 2026-09-26 — historique git » (le contenu du fichier reste exigé par le check #5, seule cette zone de liens change).
5. **Racine `ROADMAP.md`** :
   - L30 : « NE V5 package = sole directory » → marquer **ARCHIVED 2026-09-26** (→ `_archive/Submission_Package_Nature_Energy_Manuscript/`), canonique = package AE.
   - L84 : chemin `Redac_Paper2/Pistes_Improvements260625.md` → noter suppression (historique git) sans toucher aux logs de session historiques.
   - Ajouter une section **« Paper 2 — Ère Applied Energy (2026-09-23 → 09-26) »** : transfer NE décliné → package AE (audit hostile F1–F29, tour reviewer M/S appliqué, faiblesses mitigées), commits `1e6c924`, `45fc296` (archivage NE+Graphics), `98b02ba`, restructuration du jour ; états : AE 62/62 · QST 22/22 · pytest 128/1 xfailed · MS 45 pp / SM 26 pp.
6. **Racine `README.md`** : ligne « Paper 2 » du tableau de statut → « Applied Energy package ready (45 pp, audit 62/62) + QST ready (22/22) » ; vérifier la section architecture (aligner sur le nouveau descripteur Redac_Paper2 si elle cite des dossiers supprimés).
7. **`COMPARAISON_Juin_Juillet_QST_AE_260924.md`** : chemin du verdict → `backups/relaunch_20260924/canon_verdict_20260924.txt` ; ajouter un bref §« Mise à jour 2026-09-26 » (tour reviewer AE complet + restructuration, pointeurs README).
8. **`AGENTS.md`** : append d'une entrée **Session 28** (restructuration : suppressions, MD mis à jour, hash de commit) ; les lignes de table Key Files et logs de session existants sont laissés tels quels (histoire).

## 4. Vérifications (avant commit)

1. Grep de dérive dans tous les MD non-archivés : `fix_percentages|plot_local_dynamics|MASTER_AUDIT_PROMPT|Redac_Paper2/reports|_bmad-output|pull_relaunch|Graphical_Abstract.png|Manuscript_NatureEnergy_26-06-25.tex` → 0 hit non justifié.
2. `python3 verify_acceptance.py` (package AE) → **62/62** ; `python3 verify_acceptance.py` (package QST) → **22/22** (les suppressions ne cassent aucun check : re-listé §0).
3. `mamba run -n fl_qom pytest Redac_Paper2/tests -q` → **128 passed / 1 xfailed** ; `ruff check src tests scripts` → clean (code non modifié, régression de sécurité).
4. `git status` : uniquement les suppressions/déplacements/MD attendus ; `_archive/` et `.claude/` restent non tracktés.

## 5. Commit + push + rsync HPC

1. `git add Redac_Paper2 ROADMAP.md README.md AGENTS.md` (et rien d'autre) → commit `chore(Paper2): restructure Redac_Paper2, remove obsolete files, refresh MDs`.
2. Push via le remote SSH : `git push git@github.com:NanaEngo/Quantum_Agrivoltaic_PT-HOPS.git main` + `git fetch origin`.
3. rsync vers `nanaengo@100.73.21.40:~/Quantum_Agrivoltaic_PT-HOPS/` **sans `--delete` global** (le serveur possède des exclusivités : `backups/ data/ logs/ …`) :
   - fichiers modifiés : `rsync -avz --checksum --files-from` depuis `git diff --name-status` ;
   - suppressions : `ssh … rm -rf` de la liste exacte des paths supprimés (`Redac_Paper2/reports`, `Redac_Paper2/_bmad-output`, `Redac_Paper2/results`, `Redac_Paper2/references.bib`, marqueurs, fichiers des packages) — **vérifier le chemin source avant chaque commande** (convention 1 du README, incident du 25/09).
4. Vérification finale côté HPC : AE 62/62 + QST 22/22 + `ls` des répertoires supprimés (absents).

## 6. Hors périmètre (non modifié volontairement)

- `PROJECT.md` (racine, milestones QST tous DONE — historique) ; logs de session AGENTS.md antérieurs ; tout le contenu NE ère (canon NE ancien conservé dans `_archive/`) ; `_archive/` (dont 3 strays déjà notés) ; figures/ LaTeX non tracktés hors purge facultative §1 ; aucun `.tex` ni PDF du manuscrit.
