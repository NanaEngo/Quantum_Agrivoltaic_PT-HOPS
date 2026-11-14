# Redac_Paper2 — Espace de travail Paper 2 (Agrivoltaïque quantique)

Répertoire de travail du **Paper 2**, reconstruit de bout en bout comme soumission à
*Renewable Energy* (Elsevier) sur une base de preuves HPC organisée en work-packages WP1–WP6.

**État 2026-11-14** : package actif unique, tests **35/35**, main **21 pp / 50 références**,
SM **9 pp**, cover letter et highlights 1 p. chacun.

## Package actif (la seule sortie qui compte)

| Dossier | Journal cible | État (2026-11-14) |
|---|---|---|
| `Submission_Package_RenewableEnergy_Manuscript/` | *Renewable Energy* (Elsevier) | main **21 pp / 50 refs** · SM **9 pp** · cover + highlights 1 p. · tests **35/35** · `parameters.yaml` v2.5.0 |

Contenu : `RE_main_2611.tex` / `RE_SM_2611.tex` / `RE_Cover_letter_2611.tex` /
`RE_Highlights_2611.{tex,txt}`, `references.bib`, `parameters.yaml`, `figures/`,
`scripts/` (WP1–WP6), `data/` (artefacts JSON/CSV/NPZ), `tests/` (35 tests),
`docs/` (rapport d'analyse, plan de mitigation, protocole de terrain, registre
device/structure, passe adversariale, revue BMAD, réponse préventive aux relecteurs,
manifeste de release + checksums).

Commandes utiles :

```bash
cd Submission_Package_RenewableEnergy_Manuscript
make check test        # 10/10 blocs de config, 8/8 datasets, 35 tests
latexmk -pdf RE_SM_2611.tex && latexmk -pdf RE_main_2611.tex   # SM 9 pp, main 21 pp
python3 scripts/make_release_manifest.py                       # docs/CHECKSUMS_SHA256.txt
```

## Lignée historique (gelée)

Les packages **Applied Energy** (main 45 pp / SM 26 pp, audit 62/62) et **QST**
(main 20 pp / SI 30 pp, audit 22/22), ainsi que le package **Nature Energy** et le
retarget **Solar Energy V2611**, sont archivés dans `_archive/` à la racine du dépôt.
Ils ne sont plus ni édités ni vérifiés ici ; leur canon numérique (scan de volume NPoM,
`Φ_FT`, chaîne économique AE) reste consultable dans `_archive/` et dans l'historique git
(arbres `f0c0ada` / `2a16dce`).

## Note de provenance

Le canon NPoM (`Φ_FT = Γ_RC · ∫(P₃+P₄) dt`, sans préfacteur 2 ; maximum
0.0799 à V = 1.2 nm³ ; baseline passive 0.980) appartient à l'ère *Nature Energy* /
*Applied Energy*. Il est conservé dans `_archive/` comme archive de résultats et n'entre
pas dans le package *Renewable Energy*, dont la base de preuves est WP1–WP6.
