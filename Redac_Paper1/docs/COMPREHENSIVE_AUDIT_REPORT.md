# Comprehensive Audit Report: Quantum Simulation Framework Versions
**Date:** 2026-05-13  
**Versions Audited:** 260509, 260511, 260512 (Production Ready)

---

## 1. Executive Summary
This audit compares three versions of the `quantum_simulations_framework_parallel` codebase. The primary evolution across these versions is the **hardening against Out-of-Memory (OOM) errors** and the **standardization of production-grade simulation parameters** ($L=8, K=2$).

| Version | Focus | Stability |
| :--- | :--- | :--- |
| **260509** | Initial Parallelization | ⚠️ Risk of OOM (MAX_N_JOBS=10) |
| **260511** | Pipeline Refinement | ⚠️ Partial OOM Risk |
| **260512** | OOM Hardening | ✅ **Stable / Production Standard** |

---

## 2. Codebase Differences (Python Files)

### 2.1 Memory Management and Parallelization
The most significant differences lie in how `n_jobs` is calculated for the `joblib` backend.

- **260509**: Used a static `MAX_N_JOBS=10` in `constants.py`. At ~54 GB per trajectory, this could demand >500 GB RAM, causing crashes on the 128 GB server.
- **260511**: Maintained similar risks but started renaming functions for clarity.
- **260512**: Implemented a rigorous memory-aware scheduler.
  - **`modes_factor`**: Correctly scales memory estimates based on the number of bath modes (189 modes for FMO).
  - **Hard Capping**: Enforces `n_jobs=1` whenever a single trajectory exceeds ~40 GB.
  - **Constants**: `MAX_N_JOBS` was reduced to 1 for high-rigor production runs.

### 2.2 Functional Enhancements
- **Spectral Figures**: `260512` fully integrates `_generate_spectral_figure` to automate Figure 1(e) generation.
- **Type Hinting**: `260512` introduced Python 3.10+ type hints across core functions.
- **Docstrings**: `260512` uses raw strings (`r"""`) to prevent LaTeX backslash escaping issues.

---

## 3. Results Audit

### 3.1 Convergence Metrics
Auditing the CSVs in `reproducibility/results/` reveals the following:

- **Hierarchy Depth (L)**: 
  - All versions show convergence at $L=8$. 
  - **260512 Audit**: Residual MAE for $L=8$ is **3.10e-11**, demonstrating extreme numerical stability.
- **Matsubara Terms (K)**: 
  - Convergence at $K=2$ is verified.
  - **260512 Audit**: MAE for $K=2$ relative to $K=3$ is **3.32e-05**.

### 3.2 Data Integrity
- **Fallback Data**: Both `260511` and `260512` correctly quarantine "fallback" data using the `.INVALID_FALLBACK_DATA.csv` suffix.
- **Ensemble Averaging**: `260512` contains the most complete ensemble averages ($n=100$) with correct time-axis synchronization.

---

## 4. Final Package Verification (May 13)

The submission package `JPCL_Submission_Package_2026-05-13.zip` has been verified against the audited framework:

*   **Hierarchy Synchronization**: All documents (Manuscript, SI, Response) consistently report $L=8$ and $K=2$.
*   **Trace Preservation**: All production trajectories in the final ensemble maintain trace preservation within \num{1.0e-12}.
*   **Positivity**: No density matrix eigenvalues fall below \num{-1.0e-14}.
*   **Bibliographic Accuracy**: Verified that `Fleming2015` and `Scholes2015` are correctly cited and present in `references.bib`.

---

## 5. Implementation Status
All recommended refinements from the May 12 audit have been **successfully implemented**:

*   ✅ **L=8 Synchronization**: Standardized across all submission documents.
*   ✅ **siunitx v3**: All numerical values and units follow the latest LaTeX standards.
*   ✅ **Caption Refinement**: Informal "Take-home message" labels removed.
*   ✅ **AI Pattern Scrubbing**: Removed prohibited transitions and hollow intensifiers.

---
**Report finalized by Antigravity (JPCL Revision Auditor)**
