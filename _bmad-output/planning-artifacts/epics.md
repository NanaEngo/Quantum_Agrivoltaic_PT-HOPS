---
stepsCompleted: [1, 2]
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
---

# Quantum Agrivoltaic PT-HOPS - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Quantum Agrivoltaic PT-HOPS, decomposing the requirements from the PRD and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Comprehensive Theoretical Modeling of Selective Vibronic Driving + Polaron-Frame Dephasing.
FR2: Implementation of Polaron-Frame Dephasing Reduction mechanism.
FR3: Numerical solution of the Extended Anderson Hamiltonian (2-lead, single impurity).
FR4: High-Precision Simulation Engine with mandatory L=10 hierarchy depth.
FR5: MesoHOPS Adaptive Basis Logic for efficient dephasing reduction modeling.
FR6: HierarchicalEOM.jl (Julia) Solver for cross-verification.
FR7: Single Point of Entry Reproducibility via `reproducibility/main.py`.
FR8: Automated Figure Generation consistent with JPCL standards.

### NonFunctional Requirements

NFR1: Trace Preservation ($10^{-6}$) over $10^4$ fs integration.
NFR2: Mandatory Convergence Audit demonstrating L=10 sufficiency ($<1\%$ variance vs L=9).
NFR3: Population Positivity Enforcement across all time steps.
NFR4: Local Hardware Optimization for 32GB RAM workstation.
NFR5: Cross-Language Solver Parity ($<0.1\%$) for baseline $L=1$ cases.

### Additional Requirements

AR1: Centralized Parameter Synchronization via `parameters.yaml` (YAML 1.2).
AR2: Cross-Language Data Interoperability via HDF5 (`.h5`) serialization.
AR3: Numerical Validation Logic using Relative Error Threshold (Frobenius Norm).
AR4: Visual Style Guide implementation in `src/visualization/theme.py`.
AR5: Strict Environment isolation using Mamba `MesoHOP-sim`.

### UX Design Requirements

None (Visual standards are integrated into AR4 and FR8).

### FR Coverage Map

FR1: Epic 2 - Comprehensive Theoretical Modeling (Selective Vibronic Driving)
FR2: Epic 2 - Polaron-Frame Dephasing Reduction
FR3: Epic 2 - Dynamics at $L=10, K=10$
FR4: Epic 3 - Automated Convergence Audit
FR5: Epic 2 - Realistic FMO Model with Vibronic Modes
FR7: Epic 1 - Single Point of Entry Reproducibility
FR8: Epic 4 - Automated Figure Generation
NFR5: Epic 2 - PT-HOPS/SBD Implementation

## Epic List

### Epic 1: Reproducibility Infrastructure & Synchronization
Establish the central "Source of Truth" for the revision by initializing the directory structure, the `parameters.yaml` schema, and the `main.py` entry point.
**FRs covered:** FR7, AR1, AR5.

### Epic 2: High-Precision Simulation & Model Realism (PT-HOPS/SBD)
Implement the **Realistic FMO Model with Vibronic Modes** (FR5) and execute dynamics at **$L=10, K=10$** (FR3). This uses the **PT-HOPS/SBD** methodology to maintain stability within the 32GB RAM limit.
**FRs covered:** FR1, FR2, FR3, FR5, NFR1, NFR3, NFR5, AR2.

### Epic 3: Convergence & Verification Suite
Develop the automated validation layer to prove $L=10$ sufficiency ($L=10$ vs $L=9, 11$). This ensures the numerical results are "Reviewer-Proof".
**FRs covered:** FR4, NFR2, AR3.

### Epic 4: Manuscript-Ready Visualization & Reporting
Implement the JPCL-standard figure generation pipeline using the `theme.py` visual style guide.
**FRs covered:** FR8, AR4.
