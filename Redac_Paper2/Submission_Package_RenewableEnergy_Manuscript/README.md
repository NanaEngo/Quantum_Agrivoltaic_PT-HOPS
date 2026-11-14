# Paper 2 — *Renewable Energy* submission package

Self-contained submission package for **"Scale-Bridging Techno-Economic, Microclimatic, and
Open-Quantum Assessment of Semi-Transparent Organic Agrivoltaics for Sub-Saharan Perennial Crops"**
(Elsevier, *Renewable Energy*). Located at
`Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`.

**State 2026-11-14:** main **21 pp / 50 references**, Supporting Material **9 pp**, cover letter and
highlights 1 p. each, tests **35/35**, `parameters.yaml` `framework_version: 2.5.0`.
Zero LaTeX errors, zero undefined references or citations.

---

## Deliverables

| File | What it is |
|---|---|
| `RE_main_2611.tex` / `.pdf` | Manuscript (elsarticle) |
| `RE_SM_2611.tex` / `.pdf` | Supporting Material, §S1–S7 |
| `RE_Cover_letter_2611.tex` / `.pdf` | Cover letter |
| `RE_Highlights_2611.txt` (+ `.tex`) | 5 highlights, 67–80 characters each |
| `references.bib` | Bibliography (50 cited entries) |
| `parameters.yaml` | Single source of truth for every physical and economic input |
| `figures/` | 6 figures, PDF vector + PNG |

## Evidence base (WP1–WP6)

| Directory | Contents |
|---|---|
| `scripts/` | Reproduction scripts per work package (`wp1_…` climate/optics inputs, `wp2…` TMM + NESS, `wp3…` microclimate, `wp5…` TEA/LCA/Sobol, `wp6_…` figures) |
| `data/wp1…wp5/` | Primary artifacts (ERA5 series, TMM Pareto CSV/NPZ, quantum NESS summary, decade reruns, Sobol draws) plus the 2026-11-14 audits: `wind_load_screening.json`, `wp2_device_tolerance.json`, `wp5_sobol_convergence.json` |
| `tests/` | 35 integrity tests over config, datasets, optics, quantum bounds, agro, TEA/LCA, Sobol |
| `docs/` | Analysis report, mitigation register, field protocol, device/structural register, adversarial and BMAD review records, pre-emptive reviewer reply, release manifest + checksums |

## Verification and build

```bash
make check test        # 10/10 config blocks, 8/8 datasets, 35 pytest tests
latexmk -pdf RE_SM_2611.tex && latexmk -pdf RE_main_2611.tex   # SM first, then main
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
