---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish']
releaseMode: single-release
classification:
  projectType: scientific_revision
  domain: scientific
  complexity: medium
  projectContext: brownfield
inputDocuments:
  - 'AGENTS.md'
  - 'README.md'
  - 'Redac_Paper1/Theory_Journals/JPCL/Reviewers_Comments.md'
  - 'Redac_Paper1/Theory_Journals/JPCL/Reviewers_Comments_Answers.md'
  - 'Redac_Paper1/Theory_Journals/JPCL/TOC_Graphic_Spec.md'
  - 'implementation_plan.md'
  - 'https://mesohops.readthedocs.io/en/latest/'
workflowType: 'prd'
---

# Product Requirements Document - Quantum_Agrivoltaic_PT-HOPS

**Author:** Taamangtchu
**Date:** May 1, 2026

## Executive Summary

This project executes a rigorous revision of the manuscript "Quantum-Coherent Spectral Engineering in Light-Harvesting Systems" for **The Journal of Physical Chemistry Letters (JPCL)**. The revision transforms the original research into a bulletproof, submission-ready package. The primary goal is to resolve reviewer-identified gaps in theoretical framing, model realism, and numerical consistency. By reframing "Bath Engineering" as a precise two-stage mechanism—**Selective Vibronic Driving** and **Polaron-Frame Dephasing Reduction**—this work establishes a solid foundation for the future **AgroQuantPV Suite**.

### Product Differentiator
We define **Spectral Engineering** not as trivial initial state preparation, but as a unique quantum control mechanism enabled by the adaptive spectral filtering of organic photovoltaics (OPV). This approach partitions the bath into protected resonant modes, supported by a **Mandatory Convergence Audit** ($L=10$, $K=2$, proven converged at $T=295$~K) and a **Realistic FMO Spectral Density** model (12-mode Kleinekathöfer/Coker).

## Project Classification

- **Project Type:** Scientific Revision (Manuscript & Code Hardening)
- **Domain:** Scientific (Quantum Dynamics / Biophysics)
- **Complexity:** Medium (Rigorous validation and peer-review standards)
- **Project Context:** Brownfield (Revision of existing research and code)

## Success Criteria

### User Success (Reviewer & Editor Satisfaction)
- **Reviewer 1 Acceptance**: The revised theoretical section successfully defines the "Selective Vibronic Driving" mechanism. Terminology remains flexible to adopt referee suggestions if further clarification is required.
- **Editorial Verdict**: Full acceptance by **JPCL** with no further major revisions.
- **Clarity Metric**: 100% of figure labels and symbol definitions in Figures 1 and 2(a) are consistent with IUPAC conventions.

### Research & Technical Success
- **Numerical Integrity**: All publication-grade results verified at **$L=10$, $K=2$** convergence (K=2 proven sufficient at T=295 K via dedicated K-audit: MAE(K=2→K=3) < 10⁻⁶), resolving previous text/SI contradictions.
- **Validation Pass**: Model passes the **12-test validation suite** (Trace preservation, Positivity, Hierarchy convergence).
- **Reproducibility**: A single master script can regenerate all paper figures from finalized simulation data.

## Product Scope

### Single-Release Scope (Submission-Ready State)
- **Revised Manuscript & SI**: Full LaTeX update including theoretical reframing.
- **High-Impact Figures**: 300+ DPI graphics generated with CairoMakie/Matplotlib.
- **Response to Reviewers**: Comprehensive, point-by-point rebuttal (`Reviewers_Comments_Answers.md`).
- **Converged Data**: Verified simulation datasets at $L=10$.
- **Parameter Schema**: Centralized `parameters.yaml` for synchronization between main text and SI.

### Vision (Future)
- **AgroQuantPV Suite**: A modular platform for industrial-grade quantum-agronomic digital twins.

## User Journeys

### Journey 1: The Skeptical Reviewer (Dr. Elara Vance)
- **Action**: Reviews the new **Theoretical Reframing** section and the SI **Convergence Table**.
- **Outcome**: Confirms that the "Bath Engineering" ambiguity is resolved by the precise "Selective Vibronic Driving" definition and $L=10$ baseline.

### Journey 2: The Responding Author (Taamangtchu)
- **Action**: Uses the **Traceability Matrix** and **Convergence Audit tool** to manage 15+ requirements.
- **Outcome**: Submits the revision with 100% confidence that every reviewer point is addressed and the data is exact.

### Journey 3: The Future Researcher
- **Action**: Downloads the reproducibility package and follows the **Algorithm Guide** for PT-HOPS/MesoHOPS.
- **Outcome**: Successfully regenerates results on the first try, establishing the suite as a "gold standard" for open-source quantum dynamics.

## Innovation & Novel Patterns
- **Adaptive Spectral Control**: Redefining OPV panels as active quantum control tools.
- **Quantum-Agronomic Digital Twin**: Bridging the picoscale (quantum coherence) with the megascale (agricultural systems).

## Scientific & Domain Requirements
- **Peer-Review Fidelity**: Every claim traceable to specific simulation runs with recorded parameters.
- **Numerical Convergence**: Mandatory $L=10$ hierarchy depth for all final figures.
- **Physical Realism**: Mandatory use of the **Realistic FMO Spectral Density** (including vibronic modes).

## Functional Requirements

### Theoretical Modeling
- **FR1**: Formally define "Spectral Engineering" as a two-stage mechanism (Selective Vibronic Driving + Polaron Frame Dephasing), remaining open to referee refinements.
- **FR2**: Provide a mathematical derivation of coherence enhancement in the polaron frame.

### Quantum Simulation Engine
- **FR3**: Execute dynamics at $L=10$ and Matsubara truncation at $K=2$ (converged at T=295 K; ν₁ ≈ 1300 cm⁻¹ ≫ γ_D = 50 cm⁻¹). A dedicated K-convergence audit (K=1,2,3 at fixed L=10) must confirm MAE(K=2→K=3) < 10⁻⁶ before production runs.
- **FR4**: Automate a **Convergence Audit** comparing observables at $L=9, 10, 11$.
- **FR5**: Incorporate **multi-mode Kleinekathöfer/Coker spectral densities** (BChl modes + low-frequency solvent component) for realistic FMO modeling.
- **FR9**: Implement a **Parameter Optimization Suite** to explore the optimal vibronic coupling and laser excitation regimes.
- **FR10**: Define explicit **Functional Forms** for the laser pulse (envelope, phase, timing) within the simulation input.

### Visualization & Reproducibility
- **FR6**: Generate 300+ DPI figures with clearly labeled axes, legible fonts, explicit units, and **comparison traces** (not single noisy lines).
- **FR11**: Re-evaluate and correct the **Fig 2(a) Temperature Profile** to ensure physical relevance to ultrafast dynamics.
- **FR7**: Provide a **Single-Entry Script** (`reproducibility/main.py`) for paper regeneration.
- **FR8**: Centralize physical parameters in a version-controlled `parameters.yaml`.

## Non-Functional Requirements

### Accuracy & Integrity
- **Convergence Standard**: $<1\%$ variance in population dynamics between $L=10$ and $L=11$.
- **Conservation of Trace**: Total population trace maintained at **$1.000 \pm 10^{-6}$**.
- **Positivity**: Density matrix remains positive-semidefinite (${\rho} \ge 0$) at every time step.

### Performance & Integration
- **NFR4**: Local Hardware Optimization: The pipeline must run on a 128 GB RAM server and a 32 GB RAM local workstation. K=2 (21 hierarchy modes) is mandatory to prevent OOM — K=10 (77 modes) causes ~10¹¹ hierarchy states at L=10, exhausting 128 GB RAM. Memory-efficient solvers (adaptive MesoHOPS with Triangular STATIC_FILTERS and TERMINATOR=True) are required.
- **NFR5**: Algorithmic Transparency: Provide a self-contained algorithm bridge document for PT-HOPS/SBD.

## Risk Management

| Risk | Mitigation Strategy |
| :--- | :--- |
| **Reviewer Rejection of Terminology** | Ground the "Engineering" label in polaron-frame math; adapt to referee suggestions as needed. |
| **L=10 Convergence Failure** | Implement iterative step-size control and local memory optimization (<32GB). |
| **Manual Error in SI/Text Sync** | Use the Centralized Parameter Schema (`parameters.yaml`) to auto-fill LaTeX values. |
| **"Black Box" Algorithm Perception** | Provide a self-contained algorithm bridge document for PT-HOPS/MesoHOPS. |
