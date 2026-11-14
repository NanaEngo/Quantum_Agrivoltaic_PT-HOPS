# Upload checklist — *Renewable Energy* (Elsevier, ISSN 0960-1481)

**Prepared:** 2026-11-14
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

| Area | Requirement as retrieved | Package state (measured 2026-11-14) | Status |
|---|---|---|---|
| Article type | Original research paper | Original research | Pass |
| Abstract | ≤ 250 words, no references, abbreviations defined at first mention | 210 words, no citations, all abbreviations expanded | Pass |
| Keywords | 1–6, English | 6 | Pass |
| Highlights | 3–5 bullets, ≤ 85 characters each, separate editable file | 5 bullets, 67–80 plain characters, in `RE_Highlights_2611.txt`; LaTeX version in `RE_Highlights_2611.tex` | Pass, needs Word conversion |
| Graphical abstract | Encouraged; separate file, ≥ 1328 × 531 px, ≥ 300 dpi | **Not present** | Open |
| Body length | 4 000–6 000 words excluding captions and references; count stated at submission | **4 567 words** of prose (**5 886** including captions), measured on the LaTeX body with tables, figures, equations, nomenclature and references removed | Pass |
| References | ≤ 50 | **50** entries, every one cited in text or Supporting Material (22 redundant co-citations removed 2026-11-14) | Pass |
| Sections | Clearly defined, numbered, cross-references by number | Numbered by `elsarticle`; all cross-references via `cleveref` | Pass |
| Figures | Separate files, cite in order, vector or ≥ 300 dpi | 6 figures, PDF (vector) + PNG, cited in order | Pass |
| Tables | Editable, cited in order | 7 tables in LaTeX source | Pass |
| CRediT statement | Required | Present | Pass |
| Competing-interest declaration | Required | Present | Pass |
| Funding statement | Required (or explicit no-funding statement) | **Absent** | Open |
| Generative-AI declaration | Required where AI tools were used | Present | Pass |
| Data availability statement | Required | Present as prose; no repository DOI or accession | Open (see M11) |
| ORCID of corresponding author | Collected at submission | **Not recorded in the package** | Open (author input) |
| Cover letter | Required | `RE_Cover_letter_2611.tex` / `.pdf`, 1 p. | Pass |
| Source packaging | LaTeX source + PDF + class files | `elsarticle` source tree present; class file not bundled | Open |

## The two hard numeric gates — both closed on 2026-11-14

**1. References: 72 → 50.** Twenty-two redundant co-citations were removed from sentences that
already carried a primary source; no claim lost its support and no uncited entry remains in the
printed bibliography. The literature-matrix table keeps its per-stream primary citations.

**2. Body length: 7 500 → 4 567 words of prose (5 886 including captions).** The reduction came from
removing duplication rather than content: the Introduction's gap statement was compressed, the two
Discussion subsections no longer restate Results numbers already given in the same order, the
Conclusions paragraph was tightened, and three figure captions lost redundant clauses. Every headline
number and every table is unchanged.

Both counts are stated in the cover letter and in the manuscript's submission metadata. If the
journal's editorial office measures differently (for example counting table content), the measured
values above are the ones to quote.

## Remaining author inputs

1. ORCID iD for the corresponding author (S. G. Nana Engo) and co-authors.
2. Funding statement text, or confirmation that the standard "no specific grant" wording applies.
3. Graphical-abstract image (≥ 1328 × 531 px, ≥ 300 dpi) — can be assembled from `Fig3`/`Fig5`
   panels once figure permissions are settled.
4. Decision on the two numeric gates above.

## Reproducible verification commands (run before upload)

```bash
cd Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript
make check test                                   # 10/10 blocks, 8/8 datasets, 33 pytest tests
latexmk -pdf RE_SM_2611.tex && latexmk -pdf RE_main_2611.tex   # SM 9 pp, main 21 pp
grep -c "bibitem" RE_main_2611.bbl                # reference count
python3 - <<'PY'                                  # body word count
import re
t = open("RE_main_2611.tex", encoding="utf-8").read()
b = t.split("\\begin{document}")[1].split("\\bibliographystyle")[0]
for env in ("table", "figure", "equation"):
    b = re.sub(r"\\begin\{%s\}.*?\\end\{%s\}" % (env, env), "", b, flags=re.S)
print(len(re.findall(r"[A-Za-z][A-Za-z\-]+", re.sub(r"%.*", "", b))))
PY
```

## What this checklist does not establish

It records formatting and declaration compliance only. It does not claim that the editors will
accept a manuscript above the stated length and reference limits, and it does not substitute for
the field, device, and interconnection validation that the manuscript itself identifies as
outstanding.
