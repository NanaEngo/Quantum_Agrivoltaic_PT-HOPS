# Theory Journal Submission Roadmap

**Strategy:** Target computational/theoretical journals with strong quantum dynamics focus  
**Timeline:** Submission-ready  
**Status:** ✅ All manuscripts refined and compiled

---

## 📊 Target Journal Comparison

| Journal | IF | Format Class | Column | Pages | Status |
|---------|-----|-------------|--------|-------|--------|
| **J. Phys. Chem. Lett.** (Primary) | 5.7 | `achemso` | Single | 13 | ✅ Ready |
| **J. Chem. Theory Comput.** (B1) | 5.5 | `achemso` | Single | 10 | ✅ Ready |
| **Chemical Science** (B2) | 8.5 | `article` + `natbib` | Single | 6 | ✅ Ready |
| **J. Chem. Phys.** (B3) | 3.7 | `revtex4-2` preprint | Single | 9 | ✅ Ready |

---

## 📁 Folder Structure

```
Theory_Journals/
├── ROADMAP.md
├── README.md
├── generate_figures.py
├── JPCL/                          # Primary target
│   ├── Manuscript_JPCL.tex
│   ├── Manuscript_JPCL.pdf
│   ├── SI_JPCL.tex
│   ├── Cover_Letter_JPCL.tex
│   ├── Quantum_dynamics.png
│   ├── ETR_Under_Environmental_Effects.pdf
│   └── references.bib
├── JCTC/                          # Backup B1
│   ├── Manuscript_JCTC.tex
│   ├── Manuscript_JCTC.pdf
│   ├── SI_JCTC.tex
│   ├── Cover_Letter_JCTC.tex
│   ├── Quantum_dynamics.png
│   ├── ETR_Under_Environmental_Effects.pdf
│   └── references.bib
├── Chemical_Science/              # Backup B2
│   ├── Manuscript_CS.tex
│   ├── Manuscript_CS.pdf
│   ├── SI_CS.tex
│   ├── Cover_Letter_CS.tex
│   ├── Quantum_dynamics.png
│   ├── ETR_Under_Environmental_Effects.pdf
│   └── references.bib
├── JCP/                           # Backup B3
│   ├── Manuscript_JCP.tex
│   ├── Manuscript_JCP.pdf
│   ├── SI_JCP.tex
│   ├── Cover_Letter_JCP.tex
│   ├── Quantum_dynamics.png
│   ├── ETR_Under_Environmental_Effects.pdf
│   └── references.bib
└── Shared_Resources/
    └── quantum_dynamics_plots/
        ├── Quantum_dynamics.png
        └── ETR_Under_Environmental_Effects.pdf
```

---

## 🔄 Narrative Reframing per Journal

| Journal | Narrative Focus | Key Distinguishing Feature |
|---------|----------------|---------------------------|
| **JPCL** | Physical insight, coherence enhancement | Concise 5-page limit; sentence-case title; 2DES prediction |
| **JCTC** | Algorithmic innovation, computational rigor | 12-test validation suite enumerated; $\mathcal{O}(M \cdot K^L)$ scaling; memory table |
| **Chem Sci** | Multidisciplinary, biomimetic implications | "Broader context" box; ENAQT + polaron-dressing; "Conflicts of interest" |
| **JCP** | Fundamental chemical physics, polaron theory | REVTeX formatting; deep theoretical derivation; AIP Data Availability |

---

## ✅ Refinement Audit (Severe-Referee Level)

All manuscripts passed the following checks:

- [x] **AI-language removal** — no superlatives, hype, or AI-generated patterns
- [x] **Mechanism precision** — filter acts on driving field (state preparation), not on $J_{\rm bath}(\omega)$
- [x] **Consistent data** — 500 disorder realizations throughout
- [x] **Limitations section** — single-exciton manifold, site-independent baths, phenomenological trapping
- [x] **Data availability statement** — present in all four manuscripts
- [x] **Expanded references** — Tanimura (1989), Ishizaki (2009), Cao (2020), Strathearn (2018), Chin (2013), Duan (2017)
- [x] **`physics` macros** — `\ket`, `\comm`, `\Tr`, `\dd`, `\abs`, `\vb*`, `\expval`, `\dyad`
- [x] **`siunitx` macros** — `\SI`, `\SIrange`, `\SIlist`, `\si`, `\num`
- [x] **Single-column format** — all four manuscripts

---

## 📧 Suggested Reviewers (No Conflicts)

| Name | Institution | Expertise |
|------|-------------|-----------|
| Gregory Scholes | Princeton | Quantum biology, coherence |
| Alán Aspuru-Guzik | Toronto | Quantum simulations |
| Martin Plenio | Ulm | Open quantum systems |
| Graham Fleming | Berkeley | 2DES spectroscopy |
| Jianshu Cao | MIT | Energy transfer |

---

## 📅 Remaining Steps (Human-Only)

| Step | Owner | Status |
|------|-------|--------|
| Co-author review and approval | Authors | ⏳ Pending |
| Final proofreading | Authors | ⏳ Pending |
| ORCID linkage for all authors | Authors | ⏳ Pending |
| Create ACS Paragon Plus account | Corresponding author | ⏳ Pending |
| Upload and submit JPCL package | Corresponding author | ⏳ Pending |

---

**Last Updated:** March 26, 2026  
**Status:** Submission-ready across all four target journals
