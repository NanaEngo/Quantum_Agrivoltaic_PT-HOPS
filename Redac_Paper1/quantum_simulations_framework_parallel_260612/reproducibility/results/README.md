# Simulation Results & Artifacts (`results/`)
**Last updated:** 2026-06-21 (Session 8 — Cleanup: 72 credible CSVs retained)

This directory stores the primary outputs from the June 2026 simulation campaign. These artifacts serve as the basis for the figures and numerical claims in the JPCL manuscript (ID `jz-2026-00994t`).

---

## Data Validity

- All 72 CSV files are from the **L=8, K=2, SBD=3, vibronic bath** configuration.
- Trace preservation: < 5e-13. Density matrix eigenvalues: > -1e-14.
- May 2026 data (L=10, K=10, DL-only) has been removed as obsolete.

---

## Inventory (72 CSVs)

| Category | # Files | Description |
|:---|---:|:---|
| Convergence audit | 9 | L=1,2,3,6,7 + K=1,2,3 sweeps (2026-06-13) |
| Production (L=8, N=100) | 15 | Filtered + broadband + ensemble (2026-06-17/20) |
| Temperature sweep | 18 | T=285,290,300,305,310 K (2026-06-18/19) |
| Bath parameter sweep | 12 | λ=28/42, γ=40/60 (2026-06-19) |
| Filter sweep | 18 | 770/820, 730/820, 750/800, bw50, bw200, single700 (2026-06-19/20) |

## Key Results

- **Production enhancement:** η = 0.386 (Φ_filt=0.754, Φ_broad=0.544)
- **Convergence:** MAE(L=7→L=8) = 3.0e-05
- **Robustness:** η > 0 across T∈[285,310] K and λ∈[28,42] cm⁻¹

## Analysis Reports

| File | Content |
|------|---------|
| `ANALYSIS_20260617.md` | Production run |
| `ANALYSIS_20260619.md` | Phase 2 sweeps (temperature, bath, filter) |
| `ANALYSIS_20260620.md` | Phase 3 convergence finalize |

## Regeneration

```bash
mamba run -n MesoHOP-sim python ../main.py --parallel --skip-audit
mamba run -n MesoHOP-sim python ../audit_convergence.py
```

