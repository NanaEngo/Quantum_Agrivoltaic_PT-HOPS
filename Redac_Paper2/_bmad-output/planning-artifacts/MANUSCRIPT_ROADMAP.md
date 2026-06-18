# Manuscript Writing Roadmap: Paper 2
**Coordinated Vibronic Light-Harvesting & Polaritonic Interface in Quantum Agrivoltaics**

**Date:** 2026-06-18
**Target Journal:** *Nature Energy* (APC-free subscription route)
**Authors:** Teguia Kouam S.C., Goumai Vedekoi T., Tchapet Njafa J.-P., Nguenang J.-P., Nana Engo S.G.

---

## 0. Guiding Principles (from MASTER_MANUSCRIPT_STANDARD.md)

| Principle | Application |
|-----------|-------------|
| **Honesty** | All numerical claims backed by simulation output; no fabricated values |
| **Scope discipline** | Quantum dynamics → microclimate → LCA → security, no tangential excursions |
| **Transparent limitations** | Single-exciton manifold, site-independent baths, phenomenological trapping |
| **No defensive writing** | State results directly; let the data speak |
| **Zero AI-generated language** | Avoid hollow verbs (*showcases, delves*), formulaic transitions (*notably, importantly*) |
| **Journal compliance** | Nature Energy formatting (Word limit: ~5000 words main text, ~50 references) |
| **Placeholder audit** | All `[VERIFY]` markers resolved before submission |
| **Strategic citation depth** | Core references (FMO, PT-HOPS, FAO-56, BB84) + recent agrivoltaic LCA |

---

## 1. Manuscript Architecture

### 1.1 Main Manuscript (~5000 words)

| Section | Subsection | Key Results | Figures | Est. Words |
|---------|-----------|-------------|---------|------------|
| **Abstract** | — | Quantum agrivoltaics: strong coupling → 20% Φ_FT enhancement, 35% ET_c reduction, NEB > 12 kg CO2e/m²/yr | — | 200 |
| **Introduction** | Land-use conflict & spectral opportunity | OPV as active spectral shaper vs passive shade; FMO as model system; PT-HOPS/SBD framework | — | 800 |
| **Results** | **3.1 8-Site FMO + NPoM Strong Coupling** | 9×9 dressed Hamiltonian (8 FMO + 1 plasmon); g₀ > 200 cm⁻¹ at V < 1 nm³ | Fig. 1a | 600 |
| | **3.2 Quantum Dynamics & Polaritonic Transfer** | Population dynamics, RC trapping yield Φ_FT = 0.85–0.95; coherence protection via vibronic dressing | Fig. 1b–d | 700 |
| | **3.3 Dynamic NPQ Switch** | Floquet Stark detuning + OMIT modulation; 40% reduction in exciton overload at >800 W/m² | Fig. 2a–b | 500 |
| | **3.4 SERS Optomechanical Diagnostics** | Non-destructive readout: 180, 740, 1145 cm⁻¹ peaks; enhancement factor ~10² | Fig. 2c | 400 |
| | **3.5 Smart Shield Microclimate** | FAO-56 Penman-Monteith ET_c reduction; 35% shading → 28% water savings | Fig. 3a | 500 |
| | **3.6 Net Ecological Benefit** | Scenarios A vs B vs C; NEB = 12.4 kg CO2e/m²/yr (A); payback < 5 yrs (cooperative) | Fig. 3b–c | 600 |
| | **3.7 Secure IoT & QKD** | BB84 with QBER < 11%; fail-safe irrigation backup | Fig. S1 | 300 |
| **Discussion** | Quantum Divide mitigation | Tiered subsidies, cooperative models, policy recommendations | — | 600 |
| **Methods** | PT-HOPS/SBD, FAO-56, LCA, BB84 | Full parameterization and convergence criteria | — | 800 |
| **Total** | | | **3 main + 1 SI** | **~5000** |

### 1.2 Supporting Information (SI)

| Section | Content | Figures |
|---------|---------|---------|
| S1 | Hamiltonian parameterization (8-site, coupling matrix, bath decomposition) | Table S1–S2 |
| S2 | PT-HOPS/SBD convergence validation (L-sweep, K-sweep, dt-sweep) | Fig. S2–S4 |
| S3 | FAO-56 full derivation and parameterization | Table S3 |
| S4 | BB84 QBER derivation and key rate analysis | Fig. S5 |
| S5 | Cooperative economic model details | Table S4 |

### 1.3 Figure Specifications

| Figure | Description | Panels | Key Data Sources |
|--------|-------------|--------|------------------|
| **Fig. 1** | Quantum dynamics of 8-site FMO + NPoM | (a) Dressed Hamiltonian schematic; (b) Population dynamics; (c) RC yield Φ_FT; (d) Coherence lifetime | `orchestrator.py` → HDF5 → `plot_utils.py` |
| **Fig. 2** | Dynamic NPQ switch & SERS diagnostics | (a) Stark detuning vs solar flux; (b) OMIT attenuation; (c) SERS Raman spectrum | `pulse.py`, `diagnostics.py` |
| **Fig. 3** | WEF Nexus LCA comparison | (a) ET_c reduction; (b) NEB comparison A vs B vs C; (c) Cooperative payback | `fao56.py`, `neb.py`, `database.py` |
| **Fig. S1** | QKD BB84 key generation | QBER vs noise rate, key success rate | `qkd.py` |

---

## 2. Writing Workflow (BMAD Methodology)

### Phase 1: Drafting (Current Phase)
1. **Establish skeleton** → Create LaTeX file with all section headers and placeholder content
2. **Populate Results** → Insert key numerical results from simulation codebase
3. **Write Methods** → Technical descriptions of each module
4. **Frame Introduction** → Build from PRD novelty statements
5. **Craft Discussion** → Address Quantum Divide, policy implications
6. **Insert citations** → Strategic placement of key references

### Phase 2: Editorial Review
1. **Structural review** (bmad-editorial-review-structure)
   - Check logical flow: micro → meso → macro
   - Verify claims map to data
   - Eliminate redundancy
2. **Prose review** (bmad-editorial-review-prose)
   - Remove AI-isms (hollow verbs, formulaic transitions)
   - Enforce American English, serial comma
   - Verify `siunitx` v3 compliance

### Phase 3: Quality Gates (MASTER_MANUSCRIPT_STANDARD)
1. **Compilation:** `pdflatex + bibtex + pdflatex × 2` → clean build
2. **Journal compliance:** Nature Energy word limit, reference format
3. **Writing style:** `grep` banned patterns (`showcases`, `delves`, `leverage`, `robust`)
4. **LaTeX technical:** No `\\` in text, `siunitx` v3, `\cdot` for multiplication
5. **Content integrity:** Every claim cross-referenced to figure/table/SI
6. **Consistency:** Units, symbols, abbreviations throughout
7. **Placeholder audit:** Zero `[VERIFY]` or `[TODO]` remaining
8. **Citation deployment:** Strategic depth (review + primary + recent)
9. **Methodological rigor:** All simulation parameters reported
10. **Editorial board fit:** Scope alignment with *Nature Energy*

---

## 3. Key Numerical Results (from Codebase)

### Quantum Dynamics
| Parameter | Value | Source |
|-----------|-------|--------|
| FMO sites | 8 (7 + 1 extended) | `hamiltonian.py` |
| Plasmon coupling g₀ | 120–1000 cm⁻¹ (V⁻¹/² scaling) | `diagnostics.py` |
| RC trapping Γ_RC | 0.15 ps⁻¹ | `parameters.yaml` |
| Hierarchy depth L | 8 | `parameters.yaml` |
| Time step dt | 0.5 fs | `parameters.yaml` |
| Φ_FT (Scenario A) | 0.85–0.95 | `orchestrator.py` |

### Microclimate & LCA
| Parameter | Value | Source |
|-----------|-------|--------|
| Shading factor | 35% | `parameters.yaml` |
| Crop coefficient K_c | 0.85 | `parameters.yaml` |
| ET_c reduction | ~3.2 mm/day (28% vs open field) | `fao56.py` |
| NEB Scenario A | ~12.4 kg CO2e/m²/yr | `neb.py` |
| Cooperative payback | 3.5 years (5 members, 30% subsidy) | `database.py` |

### Security
| Parameter | Value | Source |
|-----------|-------|--------|
| QBER threshold | 11% (BB84 standard) | `qkd.py` |
| Key length | 256 bits | `parameters.yaml` |
| Channel noise | 5% (typical) | `parameters.yaml` |

---

## 4. Reference Strategy

### Core References (required)
- **FMO Hamiltonian:** Adolphs & Renger (2006) *Biophys. J.*
- **PT-HOPS:** Varvelo et al. (2021) *J. Chem. Phys.*; Citty et al. (2024)
- **Coherence in photosynthesis:** Engel et al. (2007) *Nature*; Panitchayangkoon et al. (2010)
- **Vibronic coupling:** Chin et al. (2013) *Nature Phys.*; Christensson et al. (2012)
- **FAO-56:** Allen et al. (1998) *FAO Irrigation and Drainage Paper 56*
- **BB84:** Bennett & Brassard (1984) *Proc. IEEE*
- **Quantum Agrivoltaics:** Vandamme et al. (2025)
- **NPoM plasmonics:** Chikkaraddy et al. (2016) *Nature*
- **OPV for agrivoltaics:** Recent *Nature Energy* / *Joule* papers on semi-transparent OPV

### Recent Literature (2024–2026)
- Latest quantum biology reviews
- Agrivoltaic LCA meta-analyses
- QKD field implementations for IoT
- SERS / cavity optomechanics advances

---

## 5. Timeline

| Milestone | Target Date | Dependencies |
|-----------|-------------|--------------|
| ✅ Context gathering | Complete | — |
| 🔄 First draft (this document) | Today | All context |
| ⬜ Structural review | Day 2 | First draft |
| ⬜ Prose polish | Day 2 | Structural review |
| ⬜ Figure production | Day 3 | Simulation pipeline |
| ⬜ Quality gates (1–10) | Day 3–4 | Draft + figures |
| ⬜ Final compilation | Day 4 | All gates passed |
