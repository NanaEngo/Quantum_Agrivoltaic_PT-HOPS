# PT-HOPS (Tutorial 03) — Minimal demo

This folder contains a pedagogical, simplified demo to illustrate the ideas behind
PT-HOPS-style stochastic unraveling for non-Markovian dynamics.

Files

- 03_pt_hops_minimal_demo.py: A minimal Python script that generates colored noise,
  integrates a toy two-level system under noisy coupling, and ensemble-averages trajectories.

Learning objectives

- See how colored noise can be discretely sampled and coupled to a system operator.
- Run ensemble trajectories and compute coarse-grained reduced dynamics.
- Understand this demo is for teaching only — the full repository contains production-quality
  HOPS/PT-HOPS implementations.

How to run

1. Activate the tutorial environment (see ../00-onboarding/environment.yaml).
2. Run the demo:

   python 03_pt_hops_minimal_demo.py

Notes

- Increase `n_traj` in the script to improve convergence (at cost of runtime).
- For instructor solutions and a Jupyter notebook version, request the notebook conversion or open a ticket in the repo.
