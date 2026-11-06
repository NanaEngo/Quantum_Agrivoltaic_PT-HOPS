# Comparaison — Ères de données Juin / Juillet & Manuscrits QST / AE

**Date :** 2026-09-24 (mise à jour 2026-09-25) · **Projet :** Quantum Agrivoltaic PT-HOPS — Paper 2
**Référentiel numérique :** canon 2026-09-23 validé contre les données brutes HPC
(voir `Submission_Package_AppliedEnergy_Manuscript/Implementation_Plan_AppliedEnergy_260923.md` §16).

> **Canon (rappel).** Φ_FT = Γ_RC ∫(P₃+P₄)dt **sans préfacteur 2**, avec
> γ_RC = 0.15 /ps, dt = 0.2 fs, 5000 pas, fenêtre 1 ps. Toute valeur stockée
> `rc_yield` supérieure à 1 est la signature du bug de double comptage de l'ère
> juillet.

---

## 1. Données HPC : ère juin vs ère juillet (vs relance septembre)

### 1.1 Tableau comparatif des runs

| # | Ère | Run / fichier HDF5 | Configuration | `rc_yield` stocké | Bug ×2 ? | Φ_FT canon | Statut |
|---|----------|--------------------|----------------|------------------:|:--------:|-----------:|--------|
| 1 | **Juin** (24 juin) | run n=100 (V=0.8, 295 K) | 9 sites, n_traj=100 | 0.0768 | non | **0.0768** | Publié — table comparative (col. NPoM-on V=0.8) ; intégré au corps des deux mains |
| 2 | **Juin** (26 juin) | `data/converged/production_dynamics.h5` (HPC main) | 295 K, n=20 | 0.080325 | non | 0.0803 | Reproduit à 1e-4 par le code corrigé (§16) |
| 3 | **Juin** | `data/converged/production_dynamics_295K_NPoM_ON.h5` (HPC main) | V=1.2 nm³, 295 K, n=20 | 0.079928 | non | **0.0799** | Point clé du papier (−91.8 % vs passif) |
| 4 | **Juin** | `data/converged/production_dynamics_77K.h5` (HPC main) | V=1.2 nm³, **77 K**, n=2 | 0.168473 | non | 0.1685 | Publié — table comparative (col. 77 K) ; facteur 2.1 ↔ +45 % (SI S8) |
| 5 | **Juillet** | `scan_A1` (V=0.2, 295 K, n=20) | scan volume | — (bloqué à 16/20 traj le 31 juil.) | (×2) | 0.0505 visé | Incomplet → remplacé par la relance 2026 |
| 6 | **Juillet** | `scan_A*` (V=0.4) | scan volume | 0.1220 | **oui** | 0.1220/2 = **0.0610** | HDF5 brut inutilisable tel quel (÷2 ou re-run) |
| 7 | **Juillet** | `scan_A*` (V=0.6) | scan volume | 0.1463 | **oui** | 0.1463/2 = **0.0731** | idem |
| 8 | **Juillet** | `scan_A*` (V=0.8) | scan volume | 0.1522 | **oui** | 0.1522/2 = **0.0761** | idem |
| 9 | **Juillet** | `baseline_N20.h5` (baseline passive, N=20) | 8 sites | **2.005642** | **oui (>1, non physique)** | — (le 0.9800 publié = `phi_ft_passive`, constante du code) | **Signature du bug** — preuve §16 |

Vérification directe du 2026-09-24 (extracteur `check_h5_vals.py`, h5py HPC) :
lignes 2, 3, 4, 9 confirmées à 0.080325 / 0.079928 / 0.168473 / 2.005642.

### 1.2 Lecture de la comparaison

- **Code de l'ère juin** : `rc_yield = γ·Σtrapped_pop·dt` — **conforme au canon**.
  Toutes les valeurs publiées (0.0768, 0.0799, 0.1685, 0.0803) proviennent de
  cette ère et n'ont jamais nécessité de correction.
- **Code de l'ère juillet** (modifié entre juin et juillet) :
  `rc_yield = 2·γ·Σtrapped_pop·dt` — **bug de double comptage**. Les trois
  volumes complétés (V=0.4/0.6/0.8) stockent exactement **2×** la valeur de
  table ; la baseline passive stocke 2.0056 (>1), impossible physiquement.
  `scan_A1` (V=0.2) n'a jamais complété (16/20 trajectoires au 31 juillet).
- **Conséquence manuscrits** : le manuscrit Nature Energy de base
  (26-06-25, ère juin) portait les bons chiffres ; le manuscrit QST daté
  26-07-29, rédigé pendant l'ère juillet, avait intégré les vintages
  contaminés ×2 (0.1599 = 2×0.0799, déficit 83.7 % = 2×(1−0.918) approché,
  0.183) — **purgés le 2026-09-23** et remplacés par le canon
  (contrôle `verify_acceptance.py` : zéro résidu).

### 1.3 Relance septembre 2026 (code corrigé, sans préfacteur)

| Relance | Volumes | Φ_FT (logs [6/10]) | Verdict canon (±0.002) | HDF5 |
|---------|---------|--------------------|------------------------|------|
| `relaunch_20260923` | 0.2→1.4 nm³ ×7 | 0.0486 / 0.0610 / 0.0731 / 0.0761 / 0.0793 / **0.0799** / 0.0791 | **7/7 OK** (V=0.8 et V=1.2 **exact** ; V=0.2 à −0.0019, à surveiller) | **0/7 écrits** — crash tardif `footprint_m2` (étape [9d/10], après le calcul de Φ_FT) |
| `relaunch_20260924` | 0.2→1.4 nm³ ×7 | = logs 0923 à ≤3e-5 | **7/7 OK** (V=0.8 = 0.076121 et V=1.2 = 0.079928 **exacts** à 5e-5 ; V0.2 −0.0019, V0.4 +0.0005, V0.6 +0.0004 ; monotonie stricte « violée » à V1.4 = repli déjà énoncé au main, pas un écart au canon) | **7/7 écrits et archivés** (`backups/relaunch_20260924/`, commit `c42b08e`) |

Points nouveaux des relances : **V=1.0 → 0.0793** (saturation) et
**V=1.4 → 0.0791** (plateau) : la série est croissante jusqu'à ≥1.2 nm³ puis
sature — jamais >1. `Phi_FT_NPoM(raw) == (physical)` partout (correction
active). φ_global = 0.9707–0.9710 (canon 0.971). **Validé par HDF5 le
2026-09-24** (verdict `backups/relaunch_20260924/canon_verdict_20260924.txt`, cohérence h5↔log ≤3e-5) —
les vintages de table **0.0795 (V1.0) / 0.0797 (V1.4), sans provenance, ont
été purgés** des deux packages au profit des moyennes n=20 mesurées.

---

## 2. Manuscrits : package QST vs package AE

Fichiers : `Submission_Package_QST_Manuscript/Manuscript_QST_26-07-29.tex`
vs `Submission_Package_AppliedEnergy_Manuscript/AppliedEnergy_main_2609.tex`.

| Aspect | **QST (IOP)** | **AE (Elsevier Applied Energy)** |
|--------|---------------|----------------------------------|
| Cible | Quantum Science and Technology (IOP, abonnement, 0 $ APC) | Applied Energy (Elsevier, route abonnement, 0 $ APC) |
| Classe LaTeX | `iopart` 12pt (`iopart.cls` fourni) | `elsarticle` [preprint,12pt] |
| Bibliographie | `unsrt` (numérotée, ordre d'apparition) | `elsarticle-num` (numérotée) |
| Main — pagination | **20 pp**, 0 erreur, 0 undefined | **38 pp** (35 + matrice de capabilities + figure-tête plateau + bloc Q1–Q3), 0 erreur, 0 undefined, 0 overfull |
| SI — pagination | **30 pp**, 0 erreur | **24 pp**, 0 erreur, 0 overfull — retitré « **Supplementary Material** » (terminologie Elsevier) |
| Sections du main | Numérotées : Introduction · Results (11 sous-sections) · Discussion (6) · Methods (8, dont Data/Code availability) | Étoilées (`\section*`) : Results (12 sous-sections) · Discussion · **Conclusions** · Methods (7) + frontmatter Elsevier |
| Spécificités AE | — | **Highlights** (`Highlights_AppliedEnergy.txt`, 5 puces ≤85 car.), **graphical abstract** conforme (2048×1024), CRediT, déclarations (conflits d'intérêts, financement, IA générative), **Nomenclature** |
| Audit d'acceptation | **`verify_acceptance.py`** (22/22 PASS, dont 5 contrôles de canon), `AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md` | **`verify_acceptance.py`** (**60/60 PASS** — canon + framing F1–F3 + novelty : Q1–Q3, matrice 7×4, figure-tête, contre-factuels 0.9/2.9 pt) |
| Passe novelty (2026-09-25) | — | Contre-factuels chiffrés dans les 3 gaps (facteur 1.6/48 ; 0.9 pt NPoM vs 2.9 pts d'écart à l'idéal) ; **matrice de capabilities 7 fonctions × 4 classes** (`tab:capability_matrix`) ; **question centrale en 1 phrase + Q1/Q2/Q3 mappées aux Results** ; **figure-tête `fig:flat_canopy`** (quenching local >90 % vs plateau global plat 0.971) ; phrase-plateau en miroir à la cover letter |
| Passe orale finale (2026-09-25) | **Complète** (abstract, intro, Discussion, figures, SI, cover) : question centrale purgée du résidu d'idiome « close this design loop » → « quantify this design trade-off end to end » ; puce-cover ~70 mots à 3 parenthèses scindée ; **5/5 reviewers vérifiés** (Mukamel, Aspuru-Guzik, Scholes, Baumberg, Olaya-Castro — emails sur sources officielles) ; audit 22/22 | **Complète** (intro, figure-tête, matrice, Discussion, Conclusions, cover — 3 passes cumulées) : sémantique 0.9/2.9 pt corrigée au rythme, parenthétique répétitive du gap (ii) retirée, digital-twin scindé ; **4/4 reviewers vérifiés** (Olaya-Castro, Yuen-Zhou, Baumberg, Barron-Gafford) ; audit 60/60 |
| Cover letter | `Cover_Letter_QST.tex` : 2 pp, EIC, route abonnement, 5 reviewers suggérés | `AppliedEnergy_Cover_letter.tex` : **1 page**, structurée sur les **5 questions** du Guide for Authors |
| Scan volume (Table 2 QST / table AE) | Canon 7 points : 0.0505 → max 0.0799 à 1.2 nm³, repli 0.0791 à 1.4 (validé n=20, relance 20260924) | Mêmes valeurs (V1.0 = 0.0793, V1.4 = 0.0791) + table comparative 4 runs + légende de cross-validation n=20 |
| Contenu spécifique | Sous-section « Experimental testability » complète | « Experimental testability » **condensée** + benchmark table **importée du package QST** ; justification **PQC-vs-BB84** dans Limitations |
| Scénario agronomique | **Horticulture seule** (benchmark tomate purgé) | idem |
| Héritage Nature Energy | `Manuscript_NatureEnergy_26-06-25.tex/.pdf` conservé en référence — **ne pas soumettre** | base PDF retirée du package (récupérable dans l'historique git) — **ne pas soumettre** |

### 2.1 Convergences (identité numérique des deux packages)

Les deux manuscrits sont **strictement alignés sur le même canon 2026-09-23** :

- Équation Φ_FT **sans préfacteur 2** (Eq. (3) main + Eq. S1 SI des deux packages) ;
- Φ_FT(V=1.2 nm³, 295 K) = **0.0799** (déficit −91.8 % vs passif) — présent
  6× dans le main AE et 5× dans le main QST ; valeurs du scan canoniques
  (0.0505 / 0.0605 / 0.0727 / 0.0768 n=100) présentes dans les deux,
  cross-validées n=20 (relance 20260924, HDF5 archivés) ;
- **Sémantique du coût d'intégration (lue au rythme, 2026-09-25)** : le NPoM
  coûte **0.9 point** de canopée (0.980 → 0.971) ; les **2.9 points** sont
  l'écart à une canopée idéale de 1.0 (dont 2.0 pts de déficit passif). Les
  premières formulations de la passe novelty attribuaient 2.9 pts au NPoM —
  corrigé partout (gaps, headline, légende, cover, figure, audit).
- Φ_global = **0.971** ; gain quantique **15 %** ; crédit eau **650 m³/yr**
  dérivé du crédit 1300 L/m²/yr (SI S5) ; sémantique η_shield = (1−η) ;
- `table_comparative_4runs.tex` : **identique bit-à-bit** dans les deux packages ;
- `references.bib` partagé (+ Brixner2005, Baumberg2019) ;
- zéro vintage obsolète (0.1599 / 83.7 % / 0.183) — vérifié par
  `verify_acceptance.py` côté QST et par l'audit §12–§16 côté AE.

### 2.2 Divergences attendues (pas des incohérences)

- Pagination différente (20 vs 35 pp) : mise en page IOP vs Elsevier +
  sections AE additionnelles (Conclusions, Nomenclature, CRediT, déclarations).
- SI plus long chez QST (30 pp) car il conserve des sections déplacées en
  Nomenclature/annexes côté AE.
- Cover letters différentes par construction (exigences éditoriales distinctes).
- Le package QST embarque l'outil d'audit d'acceptation (`verify_acceptance.py`),
  le package AE embarque les artefacts de soumission Elsevier (Highlights,
  graphical abstract, `.spl`).

---

## 3. Traçabilité

| Objet | Source |
|-------|--------|
| Preuve du bug ×2 et du canon | `Implementation_Plan_AppliedEnergy_260923.md` §16 (lignes 209–241+) |
| Valeurs h5 (0.080325 / 0.079928 / 0.168473 / 2.005642) | extraction h5py directe HPC 2026-09-24 (`check_h5_vals.py`) |
| Φ_FT relance 20260923 | `relaunch_20260923/V*/scan_vol_*.log` (étape [6/10]) + CSV `npom_scan_relaunch_20260923.csv` |
| Canon des packages | blocs « Numerical canon » des deux README |
| Structure des mains | `\section`/`\subsection` des deux `.tex` ; builds du 2026-09-23 (logs `build_main.log` / `build_si.log`) |

*Mise à jour 2026-09-25 : la relance `relaunch_20260924` est **complète et
validée** (7/7 HDF5, verdict canon OK, preuves archivées et committées) ; le
package AE est passé à 38 pp / 60 contrôles avec la passe novelty ; la
checklist d'upload est dans `Submission_Package_AppliedEnergy_Manuscript/
CHECKLIST_UPLOAD_AppliedEnergy.md` ; les **passes orales finales des deux
packages sont closes** (audits 60/60 AE et 22/22 QST, revues orales locales
et HPC) ; ORCID 4/5 collectés (Vedekoi à créer).*

---

*Mise à jour 2026-09-26 : **tour reviewer complet du package AE** (M1–M21 /
S-M1–S-M9 + N1–N25 appliqués, faiblesses mitigées, cite frauduleux remplacés,
Monte-Carlo 10⁵ avec IC 95 %, audit 62/62 local + HPC) puis
**restructuration de `Redac_Paper2/`** : suppression de `reports/`,
`_bmad-output/`, `results/`, de la bibliographie racine non utilisée, des
marqueurs one-shot et des copies ère NE du package QST ; README du workspace
et des deux packages réécrits. Le verdict canon est désormais référencé à
`backups/relaunch_20260924/canon_verdict_20260924.txt`.*
