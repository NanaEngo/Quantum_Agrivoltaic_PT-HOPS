# Upload checklist — *Renewable Energy* (Elsevier, ISSN 0960-1481)

**Prepared:** 2026-11-14 (updated 2026-11-15)
**Package audited:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`
**Closes:** mitigation item **M12** of `OUTSTANDING_REFERENCE_ARTICLE_MITIGATION_PLAN_20261113.md`

## Provenance of the requirements (read this first)

The journal's Guide for Authors at `https://www.sciencedirect.com/journal/renewable-energy/publish/guide-for-authors`
returned **HTTP 403** to automated retrieval, so its text could not be read directly. The
requirements below were transcribed from indexed excerpts of that same page (ISSN 0960-1481).
House-style items common to Elsevier titles (declarations, highlights file, graphical abstract,
numbered sections) are confirmed against the journal page excerpts too.

Consequence: **every line of the "Requirement" column must be re-read in a browser before the
upload is started.** No item below is marked verified unless it was checked against the package
artifact named beside it. Where the guide's retrieved wording is mutually inconsistent, the
discrepancy is recorded rather than resolved by guesswork.

## Status summary

| Area | Requirement as retrieved | Package state (measured 2026-11-15) | Status |
|---|---|---|---|
| Article type | Original research paper | Original research (`20 pp` main, `13 pp` SM) | Pass |
| Abstract | ≤ 250 words, no references, abbreviations defined at first mention | `243` whitespace tokens in `pdftotext RENE_main_2611.pdf` (each math fragment counting separately, prose word count lower); no citations; abbreviations expanded | Pass |
| Keywords | 1–6, English | 6 | Pass |
| Highlights | 3–5 bullets, ≤ 85 characters each, separate editable file | 5 bullets, 67–80 plain characters, in `RENE_Highlights_2611.txt` (LaTeX + PDF `RENE_Highlights_2611.tex`/`.pdf`) | Pass |
| Graphical abstract | Encouraged; separate file, ≥ 1328 × 531 px, ≥ 300 dpi | Present: `figures/Graphical_Abstract_RENE_2611.png` (`3590 × 1315 px`, `300 DPI`) + `.pdf` (`scripts/wp6_generate_graphical_abstract.py`) | Pass |
| Body length | 4 000–6 000 words excluding captions and references; count stated at submission | **4 705 words** of prose (**5 194** including captions), measured with `scripts/count_body_words.py` | Pass |
| References | ≤ 50 | **50** `\bibitem` entries in `RENE_main_2611.bbl` (`21` in `RENE_SM_2611.bbl`) | Pass |
| Sections | Clearly defined, numbered, cross-references by number | Numbered by `elsarticle`; all cross-references via `cleveref` + `xr` | Pass |
| Figures | Separate files, cite in order, vector or ≥ 300 dpi | 6 main figures (`Fig1..Fig6`, PDF vector + 600 DPI PNG), cited in order, plus Graphical Abstract | Pass |
| Tables | Editable, cited in order | 7 main tables + SM tables (`tab:sm_econ_inputs`..`tab:sm_tariff_residual`, `tab:sm_extensions`) in LaTeX source | Pass |
| CRediT statement | Required | Present in `RENE_main_2611.tex` | Pass |
| Competing-interest declaration | Required | Present in `RENE_main_2611.tex` | Pass |
| Funding statement | Required (or explicit no-funding statement) | Present: explicit no-grant statement + PenavoraServer compute acknowledgment (`Penabei Samafou`); no institutional grant claim | Pass |
| Generative-AI declaration | Required where AI tools were used | Present in `RENE_main_2611.tex` | Pass |
| Data availability statement | Required | Present in `RENE_main_2611.tex` (summary tables in SM; underlying data/scripts planned for Zenodo DOI per `ZENODO_UPLOAD_GUIDE.md`) | Pass (DOI pending) |
| ORCID of co-authors | Collected at submission | `4 of 5` ORCIDs recorded in `ZENODO_UPLOAD_GUIDE.md` (incl. corresponding author `0000-0002-7484-3508`); `T. Goumai Vedekoi` pending | Partial (4/5 recorded) |
| Cover letter | Required | `RENE_Cover_letter_2611.tex` / `.pdf`, `1 p.` (synced counts & US English) | Pass |
| Source packaging | LaTeX source + PDF + class files | Self-contained `elsarticle` source tree + PDFs + `THREE_READING_AUDIT_20261115.md` | Pass |

## The two hard numeric gates — closed (updated after Round-3 refinements)

**1. References: 72 → 50.** Co-citations were consolidated onto primary sources; Round-3 split Cameroon institutional references cleanly (`ENEO_Tariff2024`, `SOCADEL2026Decree`, `IMF2026Cameroon`, `CSPH2026Diesel` in SM; swapped 2 secondary co-citations in main text) to keep **exact `50` references** in `RENE_main_2611.bbl` and **21** in `RENE_SM_2611.bbl`.

**2. Body length: ~7 500 → 4 705 words of prose (5 194 including captions).** Well within the 4 000–6 000 word envelope (`4 466` before Round-3 Cameroon/tariff/residual refinements; `4 705` after adding those analyses). Both counts are stated in `RENE_Cover_letter_2611.tex`.

## Remaining author inputs

1. ORCID iD for `T. Goumai Vedekoi` (`4 of 5` author ORCIDs already recorded in `ZENODO_UPLOAD_GUIDE.md`).
2. Reserve/mint the Zenodo dataset DOI (`ZENODO_UPLOAD_GUIDE.md`) and paste into `Data availability` in `RENE_main_2611.tex` if publishing dataset concurrently with upload.
3. Re-read the *Renewable Energy* Guide for Authors directly in a browser before clicking submit (automated retrieval returned HTTP 403).

## Reproducible verification commands (run before upload)

```bash
cd Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript
make check test PYTHON=/home/taamangtchu/miniforge3/envs/qom/bin/python
latexmk -pdf RENE_SM_2611.tex && latexmk -pdf RENE_main_2611.tex   # SM 13 pp, main 20 pp
grep -c "bibitem" RENE_main_2611.bbl                # 50 references
python3 scripts/count_body_words.py                  # 4 705 prose / 5 194 incl. captions
```

## What this checklist does not establish

It records formatting and declaration compliance only. It does not claim that the editors will
accept a manuscript above the stated length and reference limits, and it does not substitute for
the field, device, and interconnection validation that the manuscript itself identifies as
outstanding.
