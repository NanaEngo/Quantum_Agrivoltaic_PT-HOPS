# Three-Reading Submission Audit & Mitigations (*Renewable Energy*)

**Date:** `2026-11-15` (updated after Round-3 audit & `RENE_*_2611` rename)  
**Audited Deliverables:** `RENE_main_2611.tex/.pdf`, `RENE_SM_2611.tex/.pdf`, `RENE_Cover_letter_2611.tex/.pdf`, `RENE_Highlights_2611.tex/.txt/.pdf`, `figures/Graphical_Abstract_RENE_2611.png/.pdf`, and `ZENODO_UPLOAD_GUIDE.md`.

---

## 1. Authors' Reading (Technical Fidelity, Declarations, Notation Parity)

| Check | Finding | Mitigation Applied |
|---|---|---|
| Nomenclature definitions | `LCOE` in Nomenclature table (`RE_main_2611.tex`) defined circularly as `"LCOE (USD/kWh)"`; `DPBP` not expanded at first use in §3.2 (`L305`); inconsistent `GCR \qty{40}{\percent}` notation in §2.1 | Replaced circular `LCOE` entry with `"levelized cost of electricity (USD/kWh)"`; expanded `"discounted payback period ($\mathrm{DPBP} = \qty{3.01}{\yr}$)"` in §3.2; standardized `$\mathrm{GCR}=\qty{40}{\percent}$` |
| Data availability statement | Claimed raw ERA5 hourly series and Hamiltonians were *"archived in the Supporting Material"*, overstating PDF contents vs. parameter/summary tables | Updated `Data availability` in `RE_main_2611.tex` to state accurately that parameter tables and scenario summaries are in SM while raw hourly series, TMM spectra, Hamiltonians, and scripts will be deposited on Zenodo upon publication and are available on request |
| Cross-doc metadata, Round-3 audit & zip | Updated `RENE_*_2611` naming, `wp5d` MT-tariff/Yr-20-residual bounds, `IMF2026Cameroon`/`CSPH2026Diesel`/`ENEO_Tariff2024`/`SOCADEL2026Decree` citations, and `99.8pt` table overflow on `tab:sm_tariff_residual` | Wrapped `tab:sm_tariff_residual` in `\resizebox{\textwidth}{!}`, verified `0` `\authorcheck` / `0` undefined refs, and synced `36/36` tests, `DATA_ANALYSIS_REPORT_20261113.md` §7, `ZENODO_UPLOAD_GUIDE.md`, and submission bundle |
| Author/Funding alignment | Co-author roster (`5` authors, `4` ORCIDs logged in `ZENODO_UPLOAD_GUIDE.md`, `T. Goumai Vedekoi` open), no-grant statement, and PenavoraServer compute credit (`Penabei Samafou`) | Confirmed identical wording across `RE_main_2611.tex` and `ZENODO_UPLOAD_GUIDE.md` |

---

## 2. Domain Referees' Reading (Agronomy, PV TEA/LCA, Open-Quantum)

| Lens | Finding | Mitigation / Verification |
|---|---|---|
| International PV/Policy reader | Cameroon regulatory acronyms (`ARSEL`, `CSPH`, `PPA`) appeared without first-use expansion in §5.2 (`RE_main_2611.tex:L399`) | Expanded to `Electricity Sector Regulatory Agency (ARSEL)`, `Hydrocarbon Prices Stabilization Fund (CSPH)`, and `power-purchase agreement (PPA)` without adding main-text references beyond the 50-entry ceiling |
| Graphical Abstract accuracy & clarity | Initial render showed legend/badge overlap in Panel (a), dual y-axis label crowding between (a)–(b), and contour label collision in Panel (c) | Rebuilt `scripts/wp6_generate_graphical_abstract.py` (`3590 x 1315 px` @ `300 DPI`): unified Panel (a) legend with clear headroom, centered `Sobol S_T (ΔNPV)` cleanly in open Panel (c) whitespace, widened panel spacing (`wspace=0.45`), and visually verified zero overlaps |
| Boundary & counterfactual claims | Decade (`2014–2023`) isolation, 50% export-acceptance counterfactual, `3x3` hydraulics grid (`AWC x g_b`), `R:FR` modulation sweep, and CW NESS / exact HEOM / MesoHOPS bounds | Verified consistent caveats across `RE_main_2611.tex`, `RE_SM_2611.tex`, and captions (`Attribution, not field causation`; deterministic multi-year counts) |

---

## 3. *Renewable Energy* Editor's Reading (Elsevier House & Hard Gates)

| Gate | Target / Rule | Measured Final State | Status |
|---|---|---|---|
| Abstract word count | `<= 250` words (`pdftotext` tokens) | `243` whitespace tokens (including math fragments) | **Pass** |
| Body length | `4,000–6,000` words excl. captions/refs | `4,705` clean prose words (`5,194` incl. captions) via `scripts/count_body_words.py` | **Pass** |
| Bibliography ceiling | `<= 50` references | `50` `\bibitem` entries in `RENE_main_2611.bbl` (`21` in `RENE_SM_2611.bbl`) | **Pass** |
| Highlights | `3–5` bullets, `<= 85` chars each | `5` bullets (`67–80` plain characters) | **Pass** |
| Graphical abstract | Separate image, `>= 1328 x 531 px`, `>= 300 dpi` | `3590 x 1315 px` @ `300 DPI` (`Graphical_Abstract_RENE_2611.png` + `.pdf`) | **Pass** |
| Cover letter & US English | Synced page/word counts; 1-page layout; zero UK spellings | Fixed `modelled -> modeled`; 1 page; synced `20 pp / 4,705 / 5,194 / 50 refs / 13 pp SM` | **Pass** |
| Manuscript voice rules | Zero `WP1–WP6`, repo paths, `\authorcheck`, or report jargon in `.tex` | Automated scan confirmed `0` hits in `RENE_main_2611.tex` and `RENE_SM_2611.tex` (`\authorcheck` macro removed) | **Pass** |
