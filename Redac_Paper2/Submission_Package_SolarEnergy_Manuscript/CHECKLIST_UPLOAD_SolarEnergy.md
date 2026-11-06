# Checklist d'upload — Solar Energy (Research Article)

**Date :** 2026-11-06 · **Package :** `Submission_Package_SolarEnergy_Manuscript/`
**Préambule :** seuils repris du package Applied Energy (sources secondaires, GFA non vérifié pour Solar Energy). Tout seuil marqué **[À CONFIRMER]** doit être vérifié sur l'écran correspondant du portail EM au moment de l'upload (ils y sont affichés). Le GFA de *Solar Energy* n'a pas été récupéré avant cette conversion — première action de la session d'upload : lire la page Guide for Authors sur sciencedirect.com/journal/solar-energy.

**Historique :** V2611 = retarget après refus chez Applied Energy (2026-11). Conversion 2026-11-06 : renommage des fichiers (suffixe `V2611`), patch interprétatif R1–R8 appliqué au main (`docs/REFINEMENT_INTERPRETIVE_20261106.md`), ajouts SM (ledger d'usage des terres LER ≈ 1,43 ; stress test durabilité cycle 5 ans), cover letter et highlights réécrits, `verify_acceptance.py` réaligné sur les constantes V2611 + canon interprétatif. Canon numérique inchangé.

---

## 1. Fichiers de soumission (états à re-vérifier après rebuild)

| Fichier | Rôle | État |
|---|---|---|
| `SolarEnergy_main_V2611.tex/.pdf` | Manuscrit | **rebuild en cours** ; 0 erreur visé, 0 undefined ; ~200 mots abstract ; 7 keywords ; audit V2611 à relancer |
| `SolarEnergy_SM_V2611.tex/.pdf` | Supplementary Material | **27 pp + 2 paragraphes V2611** (build à refaire) ; terminologie Elsevier « Supplementary Material » |
| `SolarEnergy_Cover_letter.tex/.pdf` | Cover letter | 1 page visée ; « Why *Solar Energy* ? », nouveauté positionnée, 4 reviewers suggérés |
| `Highlights_V2611.txt` | Highlights | 5 puces ≤ 85 caractères (standard Elsevier certain) — réécrites 2026-11-06 |
| `figures/Graphical_Abstract_wide.png` | Graphical abstract | **2048×1024** ✓ (format hérité AE ; taille SE **[À CONFIRMER]**) |
| `references.bib` | Bibliographie | 201 entrées ; ≥ 2 papiers du courant AE/SE-family cités (contrôle d'audit) ; entrées V2611 toutes vérifiées OpenAlex/Crossref |
| `verify_acceptance.py` | Audit d'acceptation | adapté V2611 — relancer après rebuild (62/62 visé) |
| `plot_plateau_canopy.py` | Source figure-tête | Régénérable (`python3 plot_plateau_canopy.py`) |

**Artefacts à ne PAS uploader** : `.aux/.log/.out/.toc/.bbl/.blg/.spl`, `Implementation_Plan_AppliedEnergy_260923.md` (historique interne), tout fichier hérité `Manuscript_NatureEnergy_*` / `AppliedEnergy_*` (le package AE d'origine vit ailleurs dans l'historique git — ne pas soumettre).

## 2. Seuils — état de conformité

| Seuil | Limite | État V2611 | Statut |
|---|---|---|---|
| Longueur du manuscrit | Solar Energy : pas de plafond dur publié **[À CONFIRMER GFA]** | ~4 000 mots post-patch (contrôle d'audit ≤ 12 000) | ✅ |
| Abstract | ≤ 300 mots **[À CONFIRMER]** | ~200 mots (réécrit argument-first) | ✅ |
| Keywords | 1–7 chez AE **[À CONFIRMER pour SE]** | **7** | ✅ — si l'écran plafonne à moins, garder les plus thématiques |
| Highlights | 5 puces × ≤ 85 car. (standard Elsevier) | 5 × ≤ 85 ✓ (à re-mesurer si retouche) | ✅ |
| Graphical abstract | Format large 2048×1024 (hérité AE) | ✓ — exiger SE **[À CONFIRMER]** | ⚠️ |
| Cover letter | 1 page | 1 page visée (rebuild) | ✅ |

## 3. ORCID — état de la collecte (2026-09-25) : **4/5 trouvés**

| Auteur | ORCID | Source de confirmation |
|---|---|---|
| Steve Cabrel **Teguia Kouam** (correspondant) | `0009-0000-7853-5476` | ✓ page ACS JPCL du Paper 1 (liée à steve.teguia@facsciences-uy1.cm) |
| Theodore **Goumai Vedekoi** | **— à créer** (orcid.org, 5 min) | Aucun ORCID public trouvé ; seule action restante |
| Jean-Pierre **Tchapet Njafa** | `0000-0002-1936-8353` | ✓ 3 sources (chemRxiv, page auteur arXiv, CRediT ResearchGate) |
| Jean-Pierre **Nguenang** | `0000-0002-7140-7196` | ✓ attribution inline Springer 2018 — à confirmer par l'auteur à la saisie EM |
| Serge Guy **Nana Engo** | `0000-0002-7484-3508` | ✓ **confirmé par l'auteur** + auto-dépôt arXiv 2026-08 |

NB Nana Engo : le metadata AIP 2017 (JCP) associe `0000-0002-3013-3029` à son nom — ancien enregistrement ou homonyme ; en cas de double compte ORCID, les fusionner via le support ORCID avant la saisie EM.

- Correspondant : **ORCID requis** au moment de la soumission EM — le relier au profil EM au step « Authors » (sinon blocage).
- Co-auteurs : ORCID individuels demandés (non bloquants chez Elsevier, mais requis pour l'affiliation crédible CRediT à la publication).
- Reste à faire avant la session : **Vedekoi crée son ORCID** et chacun lie son ORCID à l'article JPCL via le wizard « Search & link » (5 min).

## 4. Affiliations, déclarations, divers

- CRediT : présent au main (contrôle d'audit) — vérifier la correspondance avec les rôles saisis dans EM (EM demande la saisie manuelle par auteur).
- Déclarations : conflits d'intérêts ✓, financement ✓, IA générative ✓ (au main).
- Data availability : dépôt public Zenodo avec DOI réservé dès la soumission (snapshot HDF5 + script d'extraction + environment pin prêts) + périmètre (paramètres, YAML, scripts d'orchestration, code d'analyse) — cohérent avec la section du main ; ne plus attendre l'acceptation.
- Route abonnement (0 $ APC) : *Solar Energy* est un journal hybride — à la saisie EM, choisir « Subscription publication (no APC due) » ; phrase présente dans la cover letter.
- Historique éditorial : si EM demande les soumissions antérieures, déclarer Nature Energy (transfert décliné) et Applied Energy (refus) — la cover letter ne mentionne que NE, cohérent avec les pratiques ; à ajuster si le formulaire exige la liste complète.
- Reviewers suggérés (4, dans la cover letter) — **vérifiés actifs le 2026-09-25** (profils institutionnels + publications 2024–2025) :
  | Reviewer | Institution (vérifiée) | Email | Domaine |
  |---|---|---|---|
  | Alexandra **Olaya-Castro** | UCL, Dept. Physics & Astronomy (Prof., Head of Biological Physics) | **a.olaya@ucl.ac.uk** ✓ | Biologie quantique, transport excitonique |
  | Joel **Yuen-Zhou** | UC San Diego, Chem & Biochem (Prof.) | **joelyuen@ucsd.edu** ✓ | Chimie polaritonique |
  | Jeremy **Baumberg** | Cambridge, Cavendish Lab (Prof. Nanophotonics, FRS) | **JJB12@cam.ac.uk** ✓ | NPoM/SERS, nanophotonique |
  | Greg **Barron-Gafford** | U. Arizona, School of Geography (Prof.) + Biosphere 2 | **gregbg@arizona.edu** ✓ | Agrivoltaïsme, FEW nexus |
  Emails ✓ confirmés sur des pages institutionnelles officielles. Aucun n'a de conflit évident (pas de co-tutelle, pas de collaboration récente avec les auteurs). NB : Barron-Gafford est aussi co-auteur de RandleBoggis2026 et Vernier2026 citées au main — si EM signale un conflit, sortir son nom de la liste des reviewers (les trois autres restent couvrants) ; le choix est laissé à la discrétion de l'éditeur de toute façon.
- Vérifier la limite EM sur les fichiers source (LaTeX accepté ; figures embarquées OK — sinon préparer les PNG séparés de `figures/`).

## 5. Ordre de session d'upload (30–45 min)

1. Pré-vol local : `~/miniforge3/bin/conda run -n MesoHOP-sim python verify_acceptance.py` → tout PASS (fait le 2026-11-06 — voir §1 pour le statut rebuild).
2. Lire le GFA *Solar Energy* et cocher les seuils [À CONFIRMER] du §2.
3. Créer la soumission EM → type « Research Article » → titre/abstract/keywords copiés du main (7 keywords ; réduire si l'écran plafonne).
4. ORCID des auteurs (bloquant pour le correspondant) + CRediT à la saisie.
5. Upload des fichiers dans l'ordre : main → SM → cover → highlights → GA.
6. Relecture de l'écran « Build PDF » d'EM (les caractères spéciaux siunitx — nm³, kgCO₂e m⁻² yr⁻¹ — doivent ressortir propres dans le PDF de preuve).
7. Approuver et soumettre.

## 6. Post-soumission (hors scope immédiat)

- Préparer le dépôt public des données (HDF5 relaunch_20260924 déjà archivés dans `Redac_Paper2/backups/relaunch_20260924/` — snapshot Zenodo à créer).
- Suivre la route de l'article : accusé de réception EM par email.
