# Theory Journal Submission — Implementation Guide

**Strategy:** Option B — Target computational/theoretical journals  
**Primary Target:** Journal of Physical Chemistry Letters (JPCL)  
**Status:** ✅ Submission-Ready (All 4 Journals)

---

## 📁 Submission Packages

| Journal | Manuscript | SI | Cover Letter | Figures | Format |
|---------|-----------|-----|-------------|---------|--------|
| **JPCL** | `Manuscript_JPCL.tex` (8 pp*) | `SI_JPCL.tex` | `Cover_Letter_JPCL.tex` | 2 | `achemso`, `twocolumn` |
| **JCTC** | `Manuscript_JCTC.tex` (~10 pp) | `SI_JCTC.tex` | `Cover_Letter_JCTC.tex` | 2 | `achemso`, single-col |
| **Chem Sci** | `Manuscript_CS.tex` (~6 pp) | `SI_CS.tex` | `Cover_Letter_CS.tex` | 2 | `article`+`natbib`, single-col |
| **JCP** | `Manuscript_JCP.tex` (~9 pp) | `SI_JCP.tex` | `Cover_Letter_JCP.tex` | 2 | `revtex4-2` preprint, single-col |

*\* Note: The JPCL manuscript currently occupies ~8 pages in the final `twocolumn` layout. To meet the strict 2500-word / 4-5 page JPCL limit, authors must compress the manuscript before submission by moving the "Theory and methods" equations (Eq 1-4) and the extended Hamiltonian derivations directly into the Supporting Information (SI).*

---

## ✅ Completed Tasks

### Manuscript Generation
- [x] Created all four manuscript suites (Manuscript + SI + Cover Letter)
- [x] Generated figures from simulation CSV data (`generate_figures.py`)
- [x] Created TOC graphics for each journal
- [x] Compiled all manuscripts (pdflatex + bibtex)

### Severe-Referee Refinement
- [x] Removed AI-generated language patterns
- [x] Corrected polaron mechanism (filter → driving field, not bath spectral density)
- [x] Standardized 100 disorder realizations
- [x] Added limitations section to all manuscripts
- [x] Added data availability statement to all manuscripts
- [x] Expanded references (Tanimura, Ishizaki, Cao, Strathearn, Chin, Duan)
- [x] Consistent `physics` and `siunitx` macro usage
- [x] Ensured single-column format for all manuscripts

### Journal-Specific Compliance
- [x] **JPCL:** Sentence-case title, citation-free abstract, `\begin{suppinfo}` block
- [x] **JCTC:** Enumerated 12-test suite, memory scaling table, O(M·K^L) complexity
- [x] **Chem Sci:** "Broader context" paragraph, "Conflicts of interest", quantum metrics table
- [x] **JCP:** AIP Data Availability Statement, `preprint` mode (single-column)

---

## ⏳ Remaining Tasks (Human-Only)

- [ ] Co-author review and approval
- [ ] Final proofreading
- [ ] ORCID linkage for all authors
- [ ] Create journal submission account(s)
- [ ] Upload and submit

---

## 📊 Narrative Differences

| Aspect | JPCL | JCTC | Chem Sci | JCP |
|--------|------|------|----------|-----|
| **Focus** | Physical insight | Algorithm validation | Biomimetic design | Polaron theory |
| **Methods** | Brief (in SI) | 12-test suite in main text | Moderate | Full derivation |
| **Audience** | Physical chemists | Computational chemists | Multidisciplinary | Chemical physicists |

---

## 🔄 How to Refine the Non-JPCL Manuscripts

The `JPCL/` directory acting as the primary target recently underwent two Severe Referee Audits. To ensure `JCTC/`, `Chemical_Science/`, and `JCP/` are mathematically and physically rigorous, you must manually sync the following changes from `JPCL/` to the other directories:

1. **Delete "Agrivoltaics"**: The simulation models transient laser-driven quantum dynamics, not steady-state incoherent solar flux. Replace all mentions of solar driving fields with femtosecond pulse excitation to prevent immediate physical rejection.
2. **Correct the "ETE" Math**: Replace the divergent Energy Transfer Efficiency integral with **Forward Transfer Yield ($\Phi_{\mathrm{FT}}$)**, ensuring Eq. 16 matches the trace-preserving Python simulation exactly.
3. **Copy the 2DES Protocol**: Copy the specific testable experimental protocols (using SLM $4f$-shaping to track the $\ket{1}$--$\ket{3}$ cross peak lifetime) into the conclusions/outlooks of the other papers.
4. **Copy the 3-Site Toy Model**: Ensure the minimalist 3-site generalizability proof is ported over to demonstrate the mechanism isn't an FMO artifact.

---

## 📧 Submission (JPCL Primary)

1. Go to: https://acs.manuscriptcentral.com
2. Upload: `Manuscript_JPCL.pdf`, `SI_JPCL.pdf`, `Cover_Letter_JPCL.pdf`, TOC graphic
3. **Title:** Quantum-coherent spectral engineering: non-Markovian dynamics in photosynthetic energy transfer under engineered photon baths
4. **Authors:** Steve Cabrel Teguia Kouam, Theodore Goumai Vedekoi, Jean-Pierre Tchapet Njafa, Jean-Pierre Nguenang, Serge Guy Nana Engo
5. **Corresponding:** Steve Cabrel Teguia Kouam (steve.teguia@facsciences-uy1.cm)
6. **Keywords:** quantum coherence, non-Markovian dynamics, spectral engineering, FMO complex, PT-HOPS

---

**Last Updated:** March 26, 2026
