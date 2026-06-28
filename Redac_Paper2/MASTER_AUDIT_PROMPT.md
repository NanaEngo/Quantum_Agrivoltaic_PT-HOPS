# MASTER AUDIT & REFINEMENT PROMPT — PAPER 2 (NATURE ENERGY)
## Quantum Agrivoltaic Digital Twin — Full Compliance Sprint

> **How to use this file**  
> Copy the entire prompt below into a new Antigravity conversation, or paste it after `/goal` to run it as a long-horizon autonomous task.  
> Every section is self-contained; the agent MUST execute all sections in order without skipping.  
> The target state is a submission-ready package that passes all 11 quality gates in `SUBMISSION_STANDARD.md`.

---

## CONTEXT & SOURCE OF TRUTH

- **Manuscript**: `Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex`
- **Supporting Information**: `Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/SI.tex`
- **Cover Letter**: `Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/Cover_Letter.tex`
- **Bibliography**: `Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/references.bib`
- **Codebase root**: `Redac_Paper2/src/` (Python monorepo)
- **Tests**: `Redac_Paper2/tests/`
- **Improvement roadmap**: `Redac_Paper2/Pistes_Improvements260625.md` (Axes 1–16)
- **Quality standard**: `SUBMISSION_STANDARD.md` (11 quality gates)
- **AGENTS.md**: root-level operational rules (parameter canon, rsync protocol, etc.)
- **Target journal**: *Nature Energy* (single-column, 12pt, ≤8 display items in main text, 55–75 citations)

---

## PHASE 0 — GRAPHIFY KNOWLEDGE-GRAPH ANALYSIS

### 0.1 Build or update the graphify graph

Run graphify on the Paper 2 source tree to produce a persistent knowledge graph. If
`Redac_Paper2/graphify-out/graph.json` already exists and is current, run `--update`; otherwise
run a full build.

```bash
cd /home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2
graphify . --mode deep --directed --wiki
```

If graphify is not installed, install it first:
```bash
uv tool install graphifyy -q
```

Wait for completion. Read `graphify-out/GRAPH_REPORT.md`.

### 0.2 Query the graph for audit targets

Run each of the following graphify queries in sequence. Record the outputs for use in later phases:

```
graphify query "Which Python modules are orphaned (no callers from orchestrator.py)?"
graphify query "What are the most central god-nodes connecting quantum dynamics, LCA, and IoT security?"
graphify query "Which simulation parameters in constants.py are not referenced in any test?"
graphify query "Find all edges between src/quantum_interface and src/lca — are they mediated through digital_twin.py?"
graphify query "List every SI-sec label in SI.tex and every \Cref{SI-sec:*} in the manuscript — report mismatches"
```

### 0.3 Cross-community audit

Use `graphify path` to trace the shortest path between the following pairs. Report whether the
connection exists and is properly documented in the manuscript:

- `src/quantum_interface/solver.py` ↔ `src/lca/neb.py`
- `src/iot_security/gqas_standard.py` ↔ `Submission_Package_Nature_Energy_Manuscript/SI.tex`
- `src/algorithms/qaoa_optimizer.py` ↔ `parameters.yaml`
- `src/materials/quantum_mof.py` ↔ `src/lca/database.py`

---

## PHASE 1 — MANUSCRIPT TITLE REFINEMENT

### 1.1 Assess the current title

Current title (file header comment):
> *Coordinated Vibronic Light-Harvesting & Polaritonic Interface for Symbiotic Quantum Agrivoltaics*

Evaluate this title against Nature Energy editorial criteria:
- **Clarity**: does it convey the main result (not just methods) in ≤15 words?
- **Scope fit**: does it position the paper at the energy–biology–quantum nexus?
- **Novelty signal**: does it contain the differentiating innovation (NPoM polaritonics + digital twin)?
- **Searchability**: does it include keywords that reviewers and readers will search?

### 1.2 Propose three alternative titles

Generate exactly three alternatives, each ≤15 words, in the Nature Energy declarative style
(headline stating the finding, not the method). Evaluate each on all four criteria above, then
select the best and explain the choice. Apply the selected title to:

- `\title{}` macro in `Manuscript_NatureEnergy_26-06-25.tex`
- The cover letter (`Cover_Letter.tex`)
- The header comment (line 2) of both MS and SI

### 1.3 Verify the running head

Check that the `\shorttitle{}` or equivalent running-head macro (if used) is consistent with the
new title and within the journal's character limit (≤60 characters including spaces).

---

## PHASE 2 — CHEMICAL FORMULA TYPESETTING (`mhchem` / `chemformula`)

### 2.1 Audit all chemical formulae in the manuscript and SI

Search for every chemical expression currently written in raw math mode or plain text:

```bash
grep -nP '\$[A-Z][a-z]?\$|\$[A-Z][a-z]?\^|\bPb\^|\bCd[A-Z]|\bZnSe|\bCO_2\b|\bH_2O\b|\bN_2\b' \
  Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex \
  Submission_Package_Nature_Energy_Manuscript/SI.tex
```

Also scan for:
- `CO$_2$e` → should become `\ce{CO2e}` or `\ce{CO2}` with explicit context
- `Pb^{2+}` → `\ce{Pb^{2+}}`
- `CdTe/ZnSe` → `\ce{CdTe/ZnSe}`
- `2,4,5\text{-T}` pesticide → `\ce{2,4,5-T}` (trichlorophenoxyacetic acid)
- `TiO$_2$` → `\ce{TiO2}`
- `SiO$_2$`, `Au`, `Rb` (rubidium atoms in gravimetry section)
- Any organic or inorganic formula currently written with subscripts/superscripts in math mode

### 2.2 Add `mhchem` to both preambles

Add the following line to both `Manuscript_NatureEnergy_26-06-25.tex` and `SI.tex` preambles,
immediately after `\usepackage{amsmath,amssymb,amsfonts}` and **before** `\usepackage{siunitx}`:

```latex
\usepackage[version=4]{mhchem}   % chemical formulae: \ce{CO2}, \ce{Pb^{2+}}, etc.
```

**Verify** that `mhchem` v4 is compatible with the installed TeX Live distribution:
```bash
kpsewhich mhchem.sty && head -5 $(kpsewhich mhchem.sty)
```

If `mhchem` is not available, use `chemformula` instead:
```latex
\usepackage{chemformula}   % fallback: \ch{CO2}, \ch{Pb^{2+}}
```

Document which package was installed and why in this file's changelog.

### 2.3 Replace all bare chemical expressions

Perform a systematic replacement of all identified expressions, then recompile to verify zero
errors. Key substitution table:

| Original LaTeX | Replacement |
|---|---|
| `CO$_2$e` | `\ce{CO2e}` |
| `CO$_2$` | `\ce{CO2}` |
| `Pb$^{2+}$` | `\ce{Pb^{2+}}` |
| `CdTe/ZnSe` | `\ce{CdTe/ZnSe}` |
| `TiO$_2$` | `\ce{TiO2}` |
| `2,4,5\text{-}T` | `\ce{2,4,5-T}` |
| `Rb` atoms | `\ce{Rb}` |
| `Au` nanoparticle | `\ce{Au}` |
| `SiO_2` | `\ce{SiO2}` |

---

## PHASE 3 — SIUNITX V3 COMPLIANCE AUDIT

### 3.1 Run automated scan

Execute the full `SUBMISSION_STANDARD.md §11.2` automated scan for siunitx issues:

```bash
cd Submission_Package_Nature_Energy_Manuscript

# v2 syntax (must all be zero):
grep -n '\\SI{' Manuscript_NatureEnergy_26-06-25.tex SI.tex
grep -n '\\si{' Manuscript_NatureEnergy_26-06-25.tex SI.tex

# Invalid exponential notation:
grep -n '\\num{e[0-9]' Manuscript_NatureEnergy_26-06-25.tex SI.tex

# Manual degree symbol:
grep -n '\\circ\b' Manuscript_NatureEnergy_26-06-25.tex SI.tex | grep -v 'qty\|degree'

# S{} column types in tables:
grep -n 'S{' Manuscript_NatureEnergy_26-06-25.tex SI.tex

# Bare \ref:
grep -n '\\ref{' Manuscript_NatureEnergy_26-06-25.tex SI.tex | grep -v 'cref\|Cref'
```

### 3.2 Fix all violations

For every match found in §3.1, apply the correct `\qty{}{}` or `\num{}` replacement.

### 3.3 Verify `\num{}` usage for large numbers in prose

```bash
grep -nP '\b[0-9]{5,}\b' Manuscript_NatureEnergy_26-06-25.tex SI.tex | grep -v 'num{\|label\|cite\|ref\|#'
```

Replace all bare large numbers (e.g., `161\,000`) with `\num{161000}`.

---

## PHASE 4 — REAL SIMULATIONS & DATA-BACKED FIGURES/TABLES

> **Principle**: Every number in the manuscript must trace to a real simulation run or a verified
> literature value. No fabricated or placeholder data is acceptable (SUBMISSION_STANDARD §4.1).

### 4.1 Audit all display items

List every figure and table in both MS and SI. For each, record:
1. Is the underlying data from an actual simulation run (CSV in `Redac_Paper2/data/`)?
2. Is the figure generated programmatically by a script in `Redac_Paper2/src/lca/plot_utils.py`
   or `Redac_Paper2/scripts/`?
3. Does the caption state the sample size, parameters, and units?
4. Is there a matching `\label{}` and `\cref{}` cross-reference?

```bash
grep -n '\\label{fig:\|\\label{tab:' \
  Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex \
  Submission_Package_Nature_Energy_Manuscript/SI.tex
```

### 4.2 Run orchestrator and generate all simulation data

```bash
cd /home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2
mamba run -n MesoHOP-sim python main.py --config parameters.yaml 2>&1 | tee logs/orchestrator_audit_$(date +%Y%m%d).log
```

If MesoHOPS is unavailable, run in mock-solver mode and explicitly mark outputs as
`[SIMULATION: mock_solver, MesoHOPS unavailable]` in the SI footnotes.

### 4.3 Generate all figures programmatically

Required figures:

| Figure | Source data | Generator script |
|---|---|---|
| Fig. 1 — Conceptual schematic (digital twin architecture) | N/A (schematic) | `scientific-schematics` skill |
| Fig. 2 — NPoM sweep Φ_FT vs V_mode | `data/npom_sweep*.csv` | `scripts/plot_npom_sweep.py` |
| Fig. 3 — FAO-56 ET_c seasonal curve | `data/fao56_*.csv` | `scripts/plot_fao56.py` |
| Fig. 4 — LCA net ecological benefit bar chart | `data/lca_*.csv` | `scripts/plot_lca.py` |
| Fig. S1 — Full NPoM Hamiltonian convergence | `data/convergence_*.csv` | `scripts/plot_convergence.py` |
| Fig. S2 — Comparative HDF5 trace conservation | `data/hdf5_comparison.h5` | `scripts/plot_hdf5.py` |

For each figure: confirm it compiles, is referenced via `\cref{}`, and has a complete
self-contained caption ending with an italicized take-home sentence.

### 4.4 Insert missing data tables

The following tables must be present in the manuscript (MS) or SI with real simulation data:

**Table 1 (MS)** — FMO 8-site Hamiltonian (already present, verify completeness)
**Table 2 (MS)** — NPoM mode-volume sweep results: V_mode, g_0, Φ_FT, EF_SERS, SERS LOD
**Table S1 (SI)** — Full 28-pair coupling matrix
**Table S2 (SI)** — Convergence sweep (L=6,7,8; K=1,2,3; all η values)
**Table S3 (SI)** — LCA inputs and outputs (CAPEX, OPEX breakdown, NEB, payback, NPV)
**Table S4 (SI)** — QAOA vs classical dispatch comparison (energy allocation, compute time)
**Table S5 (SI)** — GQAS compliance matrix (all 16 axes vs standard requirements)

For each missing table: extract data from the relevant CSV or compute analytically, then format
using `booktabs` with units in column headers, caption above, no vertical rules.

---

## PHASE 5 — DEEP WEB RESEARCH FOR MISSING CITATIONS

Use the `research-lookup`, `literature-search-arxiv`, `literature-search-europepmc`,
`citation-management`, and `paper-lookup` skills for the following targeted literature searches.
All new citations must be added to `references.bib` with complete metadata.

### 5.1 Mandatory missing citations to resolve

| Claim in manuscript | Search query | Target journals |
|---|---|---|
| Zwitterionic coatings 90% quantum coherence 60-day field immersion | "zwitterionic coating quantum sensor biofouling marine" 2023–2026 | ACS Nano, Nat. Commun., Adv. Mater. |
| NV diamond pathogen detection biomagnetic | "nitrogen-vacancy center diamond pathogen detection in situ" 2022–2026 | Nat. Phys., PRX Quantum, Nano Lett. |
| Quantum MOF heavy-metal adsorption 300 mg/g Pb | "quantum metal-organic framework lead adsorption capacity" 2023–2026 | J. Am. Chem. Soc., Angew. Chem. |
| Si/C quantum dots as quantum fertilizer nano-priming | "quantum dot nanopriming plant growth silicon carbon" 2022–2026 | Nat. Food, Small, ACS Nano |
| QAOA energy dispatch water-food-energy nexus | "QAOA quantum approximate optimization energy scheduling nexus" 2023–2026 | npj Quantum Inf., PRX Quantum |
| Thermal shielding field-deployed quantum sensors | "thermal stabilization quantum sensor field deployment agriculture" 2022–2026 | Sensors, Rev. Sci. Instrum. |
| FAO-56 Penman-Monteith agrivoltaic greenhouse shading | "agrivoltaic FAO56 evapotranspiration shading greenhouse" 2021–2026 | Agric. Water Manag., Sol. Energy |
| GRACE-FO groundwater recharge aquifer monitoring | "GRACE-FO groundwater recharge agricultural region" 2021–2026 | Geophys. Res. Lett., Water Resour. Res. |
| GlobalGAP blockchain traceability premium floriculture | "GlobalGAP blockchain traceability floriculture supply chain" 2022–2026 | Food Policy, Comput. Electron. Agric. |
| BB84 QKD IoT resource-constrained nodes | "BB84 QKD IoT resource-constrained low-power implementation" 2022–2026 | IEEE IoT J., Quantum Sci. Technol. |

### 5.2 Citation count audit

Target: 55–75 citations in the main document.

```bash
grep -c '\\cite{' Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex
```

### 5.3 Verify citation metadata completeness

Check for incomplete BibTeX entries (missing DOI, pages, volume). Fix all preprint-only entries
by upgrading to the published version where available.

---

## PHASE 6 — AI LANGUAGE PATTERN AUDIT (SUBMISSION_STANDARD §5)

### 6.1 Run the full banned-pattern scan

```bash
# Banned AI hollow verbs and nouns
grep -niP '\b(delve|tapestry|testament|crucial|pivotal|paramount|indispensable|invaluable|unprecedented|groundbreaking|underscore|illuminate|elucidate|showcase|harness|nexus|plethora|myriad|Moreover,|Furthermore,|Notably,|Importantly,)\b' \
  Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex \
  Submission_Package_Nature_Energy_Manuscript/SI.tex \
  Submission_Package_Nature_Energy_Manuscript/Cover_Letter.tex

# Self-congratulatory phrases
grep -niP '(we demonstrate|we show|our work establishes|significantly improves|it is worth noting|it is important to note)' \
  Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex \
  Submission_Package_Nature_Energy_Manuscript/SI.tex

# Narrative clichés
grep -niP '(In today.s world|With the advent of|In recent years|In this work,|state-of-the-art [a-z])' \
  Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex \
  Submission_Package_Nature_Energy_Manuscript/SI.tex

# British English
grep -niP '\b(optimisation|parametrisation|behaviour|colour|centre|modelling|labelling|programme)\b' \
  Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex \
  Submission_Package_Nature_Energy_Manuscript/SI.tex
```

Apply surgical replacements per `SUBMISSION_STANDARD §5.2` for every hit.

### 6.2 Check Discussion section structure

The Discussion must contain, in this order:
1. Restatement of the main result as a specific number (Φ_FT^global = 0.971)
2. Comparison to closest prior work in the field (with citation)
3. A dedicated limitations paragraph (≥4 sentences)
4. Practical guidance: when to deploy NPoM sentinel, when NOT to
5. Future work list (items 1–11 in manuscript — verify all are cited)

---

## PHASE 7 — ADVERSARIAL REVIEW (16 AXES + SUBMISSION_STANDARD GATES)

### 7.1 Axis-by-axis verification

For each of the 16 axes in `Pistes_Improvements260625.md`, verify that:
- The corresponding Python module in `Redac_Paper2/src/` is implemented and has passing tests
- The corresponding SI section (`SI-sec:*`) exists and contains the theoretical derivation
- The manuscript body cites the SI section correctly with `\Cref{}`
- Numerical results (if any) are reproducible from the simulation scripts

Run the test suite:
```bash
cd /home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2
mamba run -n MesoHOP-sim python -m pytest tests/ -v --tb=short 2>&1 | tail -30
```

Target: 117/117 passing, 1 xfailed.

### 7.2 Simulate a Nature Energy desk-rejection (Gate 10.11)

Adopt the persona of a Nature Energy editorial assistant. Evaluate each criterion:

1. **Broad significance**: Does the abstract convey why a *general energy readership* cares?
2. **Quantitative novelty**: Is there a single headline number that is clearly better than prior art?
3. **Scope fit**: Does the manuscript sit unambiguously at the energy–biology–quantum intersection?
4. **Figure quality**: Would Fig. 1 and Fig. 2 pass the 3-second rule for a non-specialist editor?
5. **Reproducibility**: Is a public code repository with a DOI cited in Data Availability?
6. **Word count**: ≤5000 words main text (excluding abstract, methods, captions, references)?

For each: PASS / CONDITIONAL / FAIL, with specific corrective action for CONDITIONAL or FAIL.

### 7.3 Adversarial reviewer simulation — Reviewer 3 (quantum computing specialist)

Reviewer 3 will object to:

1. PennyLane QAOA circuit — is the circuit depth and qubit count stated? Is there a circuit
   diagram in SI? Does SI report the variational energy landscape?
2. NV diamond detection — is magnetometry sensitivity stated in T/√Hz? Comparison to shot-noise limit?
3. Thermal Shielding model — is the shielding factor derived from a physical model or asserted?
   Temperature stability specification in K?
4. PT-HOPS/SBD "numerically exact" claim — justified for 9-site NPoM dressed system?

For each objection: write the paragraph or SI subsection text that preemptively addresses it.

### 7.4 Adversarial reviewer simulation — Reviewer 2 (agronomy/LCA specialist)

Reviewer 2 will challenge:

1. Payback period 4.23 yr — is the 30% blended-finance subsidy assumption cited? Payback without subsidy?
2. FAO-56 ET_c reduction 28% — validated against field measurements or pure model output?
3. Crop yield increase 8% from OPV quantum yield — mechanistic link to horticultural yield?
4. OPEX cleaning cost $800/yr — based on published cleaning frequency study or assumption?

For each objection: provide the data, calculation, or citation. If defense requires a manuscript
edit, make it.

---

## PHASE 8 — FULL QUALITY GATE EXECUTION (SUBMISSION_STANDARD §10)

Execute all 11 quality gates in strict order. Record date, result (PASS/FAIL), and corrective
actions for each gate.

### Gate 10.1 — Compilation Gate

Full clean final sequence (SUBMISSION_STANDARD §11.1):
```bash
cd Submission_Package_Nature_Energy_Manuscript
rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot
pdflatex -interaction=nonstopmode SI.tex
pdflatex -interaction=nonstopmode Manuscript_NatureEnergy_26-06-25.tex
bibtex Manuscript_NatureEnergy_26-06-25
pdflatex -interaction=nonstopmode Manuscript_NatureEnergy_26-06-25.tex
pdflatex -interaction=nonstopmode SI.tex
bibtex SI
pdflatex -interaction=nonstopmode SI.tex
pdflatex -interaction=nonstopmode Manuscript_NatureEnergy_26-06-25.tex
```

Required: 0 errors, 0 `??`, 0 multiply-defined labels.

### Gate 10.2 — Journal Compliance Gate

- [ ] Title ≤ 15 words
- [ ] Abstract ≤ 150 words
- [ ] Keywords: 5–8 terms
- [ ] Graphical abstract: present, landscape, 3-second rule
- [ ] Author contributions (CRediT taxonomy)
- [ ] Data availability DOI present
- [ ] Funding statement present
- [ ] Competing interests present
- [ ] SI: separate compiled document

### Gate 10.3 — Style Gate

Run all §11.2 scans. Target: 0 hits each. American English throughout.

### Gate 10.4 — Technical Gate

All siunitx v3, cleveref, booktabs, mhchem checks. Target: 0 violations.

### Gate 10.5 — Content Gate

No overclaiming; limitations paragraph in Discussion; Results section free of interpretation
language; Conclusions: 3 paragraphs, fits one page, no new information.

### Gate 10.6 — Consistency Gate

Every prose number matches a table/figure. All abbreviations defined on first use:
NPoM, PT-HOPS, SBD, FMO, FAO-56, QKD, SERS, CQD, LCA, NEB, QAOA, GQAS, MPS, QKRR, ET_c,
LOD, OPEX, CAPEX, NPV.

### Gate 10.7 — Placeholder Audit Gate

```bash
grep -rn '\[VERIFY\]\|TODO\|FIXME\|TBD\|PLACEHOLDER' \
  Submission_Package_Nature_Energy_Manuscript/
```
Target: 0 matches.

### Gate 10.8 — Citation Deployment Gate

- Main document: 55–75 citations
- Tier 1 (PT-HOPS, SBD, FMO, MesoHOPS): ≥8
- Tier 2 (FMO crystal structure, NPoM experiments): ≥4
- Tier 3 (agrivoltaic reviews, quantum biology): ≥5
- Tier 4 (alternative models, classical LCA): ≥4
- Tier 5 (software papers: MesoHOPS v1.7, PennyLane, numpy, scipy): ≥4

### Gate 10.9 — Senior Reviewer Gate

Specific checks:
- "Numerically exact" PT-HOPS qualified by L=8, K=2, MAE = 3.1×10⁻¹¹
- QAOA "quantum advantage" qualified by circuit depth, qubit count, classical comparison
- Payback 4.23 yr stated with explicit assumptions
- GQAS framed as conceptual framework, not implemented standard

### Gate 10.10 — Editorial Board Gate

- GitHub + Zenodo DOI in Data Availability
- FAIR compliance statement
- Graphical abstract satisfies 3-second rule
- No scope creep: title, abstract, conclusions describe identical scope

### Gate 10.11 — Q1 Editorial Simulation Gate

Re-run Nature Energy desk-reject simulation (Phase 7.2) after all edits.
Required decision: "Send for peer review."

---

## PHASE 9 — CODEBASE FINAL CLEANUP & DOCUMENTATION

### 9.1 Resolve all orphaned modules

Any module not called from `orchestrator.py` AND not covered by a test must be:
1. Integrated into the orchestrator pipeline, or
2. Deleted with a documented git commit reason.

### 9.2 Ensure all parameters are YAML-first

Verify `parameters.yaml` contains every physical constant used in `src/`. No hardcoded literals.

### 9.3 Update AGENTS.md

After all changes:
- Session date: today (2026-06-28)
- Session number: Session 22
- List of all files edited
- New canonical values if any parameters changed
- Test count: new total

### 9.4 Compile final submission package

Clean → full 9-step compile sequence → verify 0 errors.

### 9.5 Git commit and push

```bash
cd /home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS
git add -A
git commit -m "feat(paper2): full compliance sprint — mhchem, siunitx v3, adversarial audit, 11/11 quality gates

- Phase 0: graphify knowledge graph built and queried
- Phase 1: title refined for Nature Energy declarative style
- Phase 2: mhchem[version=4] added; all chemical formulae converted
- Phase 3: siunitx v3 full compliance; 0 SI{} or si{} remaining
- Phase 4: simulation data regenerated; all figures and tables data-backed
- Phase 5: N new citations added; all 5 tiers covered
- Phase 6: 0 AI language pattern hits; 0 British English hits
- Phase 7: adversarial audit passed (16 axes); desk-reject simulation: send for review
- Phase 8: all 11 quality gates passed
- Phase 9: orphaned modules resolved; AGENTS.md updated (Session 22)"
git push origin main
```

---

## PHASE 10 — FINAL METRICS TABLE

Complete this table and save it as `Redac_Paper2/SPRINT_22_REPORT.md`:

| Metric | Before sprint | After sprint | Target | Status |
|---|---|---|---|---|
| MS pages | 18 | — | 18–25 | |
| SI pages | 25 | — | ≥25 | |
| Title words | — | — | ≤15 | |
| Abstract words | — | — | ≤150 | |
| Citations in MS | — | — | 55–75 | |
| Chemical formulae using `\ce{}` | 0 | — | 100% | |
| `\SI{}{}` violations | — | 0 | 0 | |
| AI pattern hits | — | 0 | 0 | |
| British English hits | — | 0 | 0 | |
| `[VERIFY]` placeholders | 0 | 0 | 0 | |
| Compilation errors | 0 | 0 | 0 | |
| Undefined references `??` | — | 0 | 0 | |
| pytest passed / total | 117/117 | — | 117/117 | |
| Quality gates passed | 10/11 | — | 11/11 | |
| Desk-reject simulation | — | Send for review | Send for review | |
| Git commit | c432dfd | — | — | |

---

## APPENDIX A — CHEMICAL FORMULAE REFERENCE

| Entity | `\ce{}` expression | Context |
|---|---|---|
| Carbon dioxide (carbon footprint) | `\ce{CO2e}` or `\ce{CO2}` | LCA NEB calculations |
| Lead ion (CQD detection) | `\ce{Pb^{2+}}` | Axe 4 SERS/CQD section |
| Cadmium telluride/zinc selenide QDs | `\ce{CdTe/ZnSe}` | CQD sensor description |
| Titanium dioxide (Mie resonance) | `\ce{TiO2}` | Discussion: dielectric alternatives |
| 2,4,5-Trichlorophenoxyacetic acid | `\ce{2,4,5-T}` | Pesticide detection Axe 4 |
| Gold nanostructure | `\ce{Au}` | NPoM picocavity description |
| Rubidium (gravimeter atoms) | `\ce{Rb}` | Axe 8 quantum gravimetry |
| Silicon quantum dot | `\ce{Si}` QD | Axe 5 quantum fertilizer |
| Nitrate ion | `\ce{NO3^{-}}` | MOF adsorption Axe 11 |
| Mercury ion | `\ce{Hg^{2+}}` | MOF detection Axe 11 |
| Carbon quantum dot | CQD (abbreviation, not a formula) | First use: define in text |
| Chlorophyll *a* | Chl *a* (italic *a*, not a chemical formula) | SERS diagnostic Axe 4 |

---

## APPENDIX B — KEY MACROS TO ADD TO PREAMBLE

Add to both MS and SI preambles (after `\usepackage{mhchem}`):

```latex
% ---- Method and entity macros (single source of truth) ----
\newcommand{\PTHOPS}{PT-HOPS\xspace}
\newcommand{\SBD}{SBD\xspace}
\newcommand{\NPoM}{NPoM\xspace}
\newcommand{\FMO}{FMO\xspace}
\newcommand{\FAOsixty}{FAO-56\xspace}
\newcommand{\QKD}{QKD\xspace}
\newcommand{\SERS}{SERS\xspace}
\newcommand{\CQD}{CQD\xspace}
\newcommand{\NEB}{NEB\xspace}
\newcommand{\QAOA}{QAOA\xspace}
\newcommand{\GQAS}{GQAS\xspace}
\newcommand{\CAPEX}{CAPEX\xspace}
\newcommand{\OPEX}{OPEX\xspace}
\newcommand{\NPV}{NPV\xspace}
% ---- Physics shorthands ----
\newcommand{\PhiFT}{\Phi_{\mathrm{FT}}\xspace}
\newcommand{\PhiFTglobal}{\Phi_{\mathrm{FT}}^{\mathrm{global}}\xspace}
\newcommand{\gzero}{g_0\xspace}
\newcommand{\Vmode}{V_{\mathrm{mode}}\xspace}
\newcommand{\Ksv}{K_{\mathrm{SV}}\xspace}
```

After adding macros: do a find-and-replace pass for consistency.

---

## APPENDIX C — GRAPHIFY QUERY CHEAT SHEET

```
# Always check the knowledge graph before writing code or text:
graphify query "Does src/materials/quantum_mof.py have edges to SI.tex section on MOF?"
graphify query "Is QUANTUM_FERTILIZER_BOOST referenced in any test?"
graphify query "What is the shortest path from NPoM sensing to FAO56 water savings?"
graphify query "List all functions in orchestrator.py and which modules they call"
graphify explain "GQASComplianceMatrix"
graphify path "src/algorithms/qaoa_optimizer.py" "Submission_Package_Nature_Energy_Manuscript/SI.tex"
```

---

## CHANGELOG

| Date | Change |
|---|---|
| 2026-06-28 | v1.0 — Initial prompt generated from Pistes_Improvements260625.md + SUBMISSION_STANDARD.md |

---

*Generated: 2026-06-28 — Quantum Agrivoltaic PT-HOPS, Paper 2 (Nature Energy)*
*Apply with `/goal` for full autonomous execution. Estimated runtime: 4–6 hours.*
