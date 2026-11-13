# Simulation Workflows & Pipelines (`pipelines/`)

This directory contains high-level, reproducible workflows designed to automate 
the generation of publication-ready data for the JPCL manuscript. Each pipeline 
is self-contained, metadata-aware, and implements the structural rigor 
required for peer-reviewed research.

---

## 📂 Production Workflows

### 1. `jpcl_resubmission/` — Main Ensemble Dynamics
The primary pipeline for generating the $L=8, K=2$ production results. It 
orchestrates the full FMO ensemble dynamics, including disorder realizations 
and ensemble averaging.
- **Entry Point**: `python -m pipelines.jpcl_resubmission.main`
- **Output**: Full population kinetics and coherence data for Figure 1.

### 2. `convergence_audit/` — Numerical Rigor Validation
Systematically verifies the convergence of the hierarchy depth ($L$) and 
Matsubara terms ($K$) to address reviewer concerns regarding numerical stability.
- **Entry Point**: `python -m pipelines.convergence_audit.audit`
- **Output**: Relative error (MAE) trends for $L \in \{7, 8, 9\}$ and $K \in \{1, 2, 3\}$.

### 3. `temperature_sweep/` — Environmental Robustness
Simulates Energy Transfer Efficiency (ETE) across a broad temperature range 
to quantify the robustness of the agrivoltaic spectral engineering.
- **Entry Point**: `python -m pipelines.temperature_sweep.sweep`
- **Output**: Sensitivity traces and enhancement factors ($\eta$) for Figure 2.

---

## 🛠️ Design Principles

- **Seeded Reproducibility:** Every execution uses fixed random seeds and 
  logs the active Git SHA to ensure absolute data provenance.
- **Failure Resilience:** Critical long-running tasks implement checkpointing 
  and resume logic to handle HPC walltime limits or hardware interrupts.
- **Automated Validation:** Each workflow includes a post-execution audit 
  pass to verify physical constraints (e.g., population positivity, trace preservation).

---
**Last Updated:** 2026-05-11  
**Status:** Validated Pipelines (jz-2026-00994t)

