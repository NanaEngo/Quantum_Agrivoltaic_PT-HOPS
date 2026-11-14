# Quantum-Enhanced Agrivoltaics — Paper 1 (JPCL)

> **Last updated:** 2026-11-14 · **Status:** published (`jz-2026-00994t`, 2026-09-23)

Selective vibronic excitation for coherent transport in the FMO complex, *The Journal of Physical
Chemistry Letters*. This directory indexes the documentation around a **closed** submission; it is
not an active workspace.

## Where the citable material is

| What | Path |
|---|---|
| Published submission package (manuscript, SI, response, cover letter, figures, bib) | `Redac_Paper1/JPCL_Submission_Package_2026-06-20/` |
| Reviewer comments and formatting requests | `Redac_Paper1/JPCL_Submission_Package_2026-06-20/Reviewers_Comments_260611.md` |
| Post-publication Xiang reply draft (SBD/SI reproducibility query) | `Redac_Paper1/docs/Xiang/Response_to_Tianfu_Xiang.md` |
| June-2026 simulation synthesis | `Redac_Paper1/SYNTHESE_SIMULATIONS_JUIN2026.md` |
| Cluster launch notes | `Redac_Paper1/How-to-launch-server.md`, `run_cluster*.sh` |
| Canonical framework used for the results | `quantum_simulations_framework/` (repo root) |

Manuscripts, SI, and the response letter live in the dated package directory; nothing here
duplicates them.

## Numbers that define the published paper

- PT-HOPS with SBD = 3 bundles per site, `L = 8`, `K = 2`, `Δt = 0.5 fs`, 295 K,
  12 vibronic modes (Kleinekathöfer/Coker).
- 200/200 production trajectories, η = 0.39 ± 0.04.
- Hierarchy convergence: η(L=6) = 0.74831, η(L=7) = 0.74912, η(L=8) = 0.74915 (MAE 3.0 × 10⁻⁵).
- Per-trajectory footprint ≈ 54 GB at production settings; the memory-aware scheduler exists for
  this reason.

## What has moved away from here

The parallel-era code trees formerly referenced from this folder
(`quantum_simulations_framework_parallel_2605xx/`, `quantum_simulations_framework_parallel_260612/`,
`Theory_Journals_main/`) are **gone from the active tree**. They were either deleted as deprecated
duplicates or moved to the repository-level `_archive/` on 2026-11-06. Do not recreate them; use
`quantum_simulations_framework/` at the repo root.

## Open item

The Xiang reply is the only live action for Paper 1: decide between a private reply and an erratum.
Draft: `Redac_Paper1/docs/Xiang/Response_to_Tianfu_Xiang.md`.
