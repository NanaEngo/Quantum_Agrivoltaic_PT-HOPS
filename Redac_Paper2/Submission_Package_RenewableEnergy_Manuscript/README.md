# Paper 2 — *Renewable Energy* submission package

Self-contained submission package for **"Semi-Transparent Organic Agrivoltaics for Cameroonian Perennial Crops: Seasonal Shade Response, Cooperative Techno-Economics, and a Bound on Quantum-Coherence Effects"**
(Elsevier, *Renewable Energy*). Located at
`Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`.

**State 2026-11-15:** main **20 pp / 4,705 prose words (5,194 incl. captions) / 50 references**, Supporting Material **13 pp / 21 references**, cover letter and
highlights **1 p.** each, Graphical Abstract **`3590 x 1315 px` @ `300 DPI`**, tests **36/36**, `parameters.yaml` `framework_version: 2.5.0`.
Zero LaTeX errors, zero undefined references or citations.

---

## Deliverables

| File | What it is |
|---|---|
| `RENE_main_2611.tex` / `.pdf` | Manuscript (`elsarticle`, `20 pp`, `50` refs) |
| `RENE_SM_2611.tex` / `.pdf` | Supporting Material, `§S1–S9` (`13 pp`, `21` refs) |
| `RENE_Cover_letter_2611.tex` / `.pdf` | Cover letter (`1 p.`) |
| `RENE_Title_page_2611.tex` / `.pdf` | Elsevier Title Page with authors, affiliations, ORCIDs (`4/5`), CRediT & declarations (`1 p.`) |
| `RENE_Declaration_of_interest_2611.tex` / `.pdf` | Standalone Declaration of Interest, Funding & Generative-AI Statement (`1 p.`) |
| `RENE_Abstract_2611.docx` | Standalone Word abstract (`219` words) + title & 6 keywords |
| `RENE_Highlights_2611.txt` (+ `.tex`/`.pdf`) | 5 highlights, 67–80 characters each (`1 p.`) |
| `figures/Graphical_Abstract_RENE_2611.png` / `.pdf` | Landscape Graphical Abstract (`3590 x 1315 px`, `300 DPI`; script: `scripts/wp6_generate_graphical_abstract.py`) |
| `ZENODO_UPLOAD_GUIDE.md` | Author ORCIDs (`4/5` recorded), Editorial Manager & Zenodo metadata guide |
| `references.bib` | Bibliography (`50` main / `21` SM cited entries) |
| `parameters.yaml` | Single source of truth for every physical and economic input |
| `figures/` | 6 main figures (`Fig1..Fig6`, PDF vector + PNG) + Graphical Abstract |

## Evidence base (WP1–WP6)

| Directory | Contents |
|---|---|
| `scripts/` | Reproduction scripts per work package (`wp1_…` climate/optics inputs, `wp2…` TMM + NESS, `wp3…` microclimate, `wp5…` TEA/LCA/Sobol + `wp5d_tariff_residual_sensitivity.py`, `wp6_…` figures + Graphical Abstract) |
| `data/wp1…wp5/` | Primary artifacts (ERA5 series, TMM Pareto CSV/NPZ, quantum NESS summary, decade reruns, Sobol draws) plus the audits: `wind_load_screening.json`, `wp2_device_tolerance.json`, `wp5_sobol_convergence.json`, `wp5_export_acceptance_sensitivity_20261114.csv`, `wp5d_tariff_residual_sensitivity.json` |
| `tests/` | 36 integrity tests over config, datasets, optics, quantum bounds, agro, TEA/LCA, Sobol, and Round-3 tariff/residual sensitivities |
| `docs/` | Analysis report, mitigation register, field protocol, device/structural register, adversarial/BMAD/three-reading audits, pre-emptive reviewer reply, release manifest + checksums |

## Verification and build

```bash
make check test PYTHON=/home/taamangtchu/miniforge3/envs/qom/bin/python
latexmk -pdf RENE_SM_2611.tex && latexmk -pdf RENE_main_2611.tex   # SM first, then main
latexmk -pdf RENE_Cover_letter_2611.tex RENE_Highlights_2611.tex RENE_Title_page_2611.tex RENE_Declaration_of_interest_2611.tex
python3 scripts/make_release_manifest.py                       # docs/CHECKSUMS_SHA256.txt
```

Build artefacts (`*.aux`, `*.log`, `*.out`, `*.spl`, `*.bbl`, `*.blg`) are not kept in the package;
only the compiled PDFs are.

## Boundaries a reader should know

No paired field trial, no independent optical measurement of the stack, no structural design check,
and no bankable interconnection study exists for these three sites. The package states that
explicitly in the manuscript and quantifies what such validation would have to show; see
`docs/FIELD_VALIDATION_PROTOCOL_20261114.md`, `docs/DEVICE_STRUCTURAL_VALIDATION_REGISTER_20261114.md`,
and `docs/RESPONSE_TO_REVIEWERS_PREEMPTIVE_20261114.md`.

Superseded lineages (Nature Energy → Applied Energy → Solar Energy) are in the repository-level
`_archive/`, not here.
