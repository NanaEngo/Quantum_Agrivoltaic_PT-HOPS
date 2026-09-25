# Checklist d'upload — Applied Energy (Research Article)

**Date :** 2026-09-25 · **Package :** `Submission_Package_AppliedEnergy_Manuscript/`
**Préambule :** le GFA officiel Applied Energy renvoyait 403 lors de la rédaction
(2026-09-24) — les seuils ci-dessous proviennent de sources secondaires sauf
mention contraire. Tout seuil marqué **[À CONFIRMER]** doit être vérifié sur
l'écran correspondant du portail EM au moment de l'upload (ils y sont affichés).

---

## 1. Fichiers de soumission (états vérifiés le 2026-09-25)

| Fichier | Rôle | État |
|---|---|---|
| `AppliedEnergy_main_2609.tex/.pdf` | Manuscrit | **38 pp**, 0 erreur / 0 undefined / 0 overfull ; abstract 159 mots ; 8 keywords ; 60/60 audit |
| `AppliedEnergy_SM_2609.tex/.pdf` | Supplementary Material | **24 pp**, 0 erreur / 0 undefined ; retitré « Supplementary Material » (terminologie Elsevier) |
| `AppliedEnergy_Cover_letter.tex/.pdf` | Cover letter | **1 page**, structurée sur les 5 exigences GFA (novelty / audience / importance / langue / reviewers) |
| `Highlights_AppliedEnergy.txt` | Highlights | 5 puces ≤ 85 caractères (standard Elsevier certain) |
| `figures/Graphical_Abstract_wide.png` | Graphical abstract | **2048×1024** ✓ (contrôle d'audit `png_size`) |
| `references.bib` | Bibliographie | ≥ 2 papiers Applied Energy cités (contrôle d'audit) |
| `verify_acceptance.py` | Audit d'acceptation | **60/60 PASS** (local ET HPC) — à relancer après toute retouche |
| `plot_plateau_canopy.py` | Source figure-tête | Régénérable (`python3 plot_plateau_canopy.py`) |

**Artefacts à ne PAS uploader** : `.aux/.log/.out/.toc/.bbl/.blg/.spl`,
`Manuscript_NatureEnergy_26-06-25.*` (référence héritée — ne pas soumettre).

## 2. Seuils GFA — état de conformité

| Seuil | Limite (source secondaire) | État AE | Statut |
|---|---|---|---|
| Longueur du manuscrit | ~12 000 mots hors refs/captions **[À CONFIRMER]** | ~2 800 mots (dé-TeX brut, contrôle d'audit) — marge énorme | ✅ |
| Abstract | ≤ 300 mots **[À CONFIRMER]** | **159 mots** | ✅ |
| Keywords | 6–8 **[À CONFIRMER]** (certain plafonds à 5–6) | **8** | ⚠️ vérifier à l'upload — si plafond 6, déplacer 2 vers les highlights |
| Highlights | 5 puces × ≤ 85 car. (standard Elsevier) | 5 × ≤ 85 ✓ | ✅ |
| Graphical abstract | 2048×1024 px min, lisible en vignette | 2048×1024 ✓ | ✅ |
| Cover letter | 1 page, 5 exigences GFA | 1 page ✓ | ✅ |

## 3. ORCID — **bloquant l'upload** (TODO auteur F11)

- Correspondant (Steve Cabrel Teguia Kouam) : **ORCID requis** au moment de la
  soumission EM — en créer/relier sur le profil EM sinon blocage au step « Authors ».
- Co-auteurs : ORCID individuels demandés (non bloquants chez Elsevier, mais
  requis pour l'affiliation crédible CRediT à la publication).
- À préparer AVANT la session d'upload : collecter les 5 ORCID (ou créations
  en 5 min sur orcid.org) et les emails institutionnels de chaque auteur.

## 4. Affiliations, déclarations, divers

- CRediT : présent au main (contrôle d'audit) — vérifier la correspondance
  avec les rôles saisis dans EM (EM demande la saisie manuelle par auteur).
- Déclarations : conflits d'intérêts ✓, financement ✓, IA générative ✓ (au main).
- Data availability : engagement de dépôt public à l'acceptation + périmètre
  (paramètres, YAML, scripts d'orchestration, code d'analyse) — cohérent avec
  la section du main ; préparer le dépôt (Zenodo/GitHub) pour ne pas y revenir
  en révision.
- Route abonnement (0 $ APC, Research4Life Group A) : le dire à la cover si
  l'écran EM propose le choix OA — « Subscription publication (no APC due) »
  figure déjà dans la cover letter.
- Reviewers suggérés (4, dans la cover letter) — **vérifiés actifs le 2026-09-25**
  (profils institutionnels + publications 2024–2025) :
  | Reviewer | Institution (vérifiée) | Email | Domaine |
  |---|---|---|---|
  | Alexandra **Olaya-Castro** | UCL, Dept. Physics & Astronomy (Prof., Head of Biological Physics) | **a.olaya@ucl.ac.uk** ✓ | Biologie quantique, transport excitonique |
  | Joel **Yuen-Zhou** | UC San Diego, Chem & Biochem (Prof.) | **joelyuen@ucsd.edu** ✓ | Chimie polaritonique |
  | Jeremy **Baumberg** | Cambridge, Cavendish Lab (Prof. Nanophotonics, FRS) | **JJB12@cam.ac.uk** ✓ | NPoM/SERS, nanophotonique |
  | Greg **Barron-Gafford** | U. Arizona, School of Geography (Prof.) + Biosphere 2 | **gregbg@arizona.edu** ✓ | Agrivoltaïsme, FEW nexus |
  Emails ✓ confirmés sur des pages institutionnelles officielles (UCL MAPS
  2022 + page quantum UCL pour Olaya-Castro — le format « a.olaya-castro@ »
  deviné initialement était faux ; page profil Cavendish pour Baumberg).
  Aucun n'a de conflit évident (pas de co-tutelle, pas de collaboration
  récente avec les auteurs).
- Vérifier la limite EM sur les fichiers source (LaTeX accepté ; figures
  embarquées OK — sinon préparer les PNG séparés de `figures/`).

## 5. Ordre de session d'upload (30–45 min)

1. Pré-vol local : `python3 verify_acceptance.py` → 60/60 (fait : 2026-09-25).
2. Créer la soumission EM → type « Research Article » → titre/abstract/keywords
   copiés du main (abstract 159 mots ; keywords : si l'écran plafonne à 6,
   garder les 6 les plus thématiques et reporter les autres).
3. ORCID des auteurs (bloquant) + CRediT à la saisie.
4. Upload des fichiers dans l'ordre : main → SM → cover → highlights → GA.
5. **Confirmer sur place** les seuils [À CONFIRMER] du §2 (mots, keywords) ;
   ajuster si l'écran diffère, puis relancer l'audit après retouche.
6. Relecture de l'écran « Build PDF » d'EM (les caractères spéciaux siunitx —
   nm³, kgCO₂e m⁻² yr⁻¹ — doivent ressortir propres dans le PDF de preuve).
7. Approuver et soumettre.

## 6. Post-soumission (hors scope immédiat)

- Préparer le dépôt public des données (HDF5 relaunch_20260924 déjà archivés
  dans `Redac_Paper2/backups/relaunch_20260924/` — snapshot Zenodo à créer).
- Suivre la route de l'article : déclaration de conforms GFA reçue par email.
