# Release manifest and one-command reproduction — package state 2026-11-14

**Closes:** mitigation item **M11** (*local* part only; the durable DOI archive remains external).
**Scope:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`

## What exists now

| Element M11 asks for | Present | Artifact |
|---|---|---|
| Source code | Yes | `scripts/wp1`–`wp6`, `scripts/check_config.py`, `scripts/make_release_manifest.py` |
| Exact environment lock | Yes | `docs/environment_lock_MesoHOP-sim.yml` |
| Parameter configuration | Yes | `parameters.yaml`, `framework_version: 2.5.0` |
| Seeds and sampling scheme | Yes | `parameters.yaml` (`monte_carlo.n_samples: 10000`, `random_seed: 42`); scramble and ladder in `docs/../scripts/wp5c_sobol_convergence.py` |
| Checksums of inputs and outputs | Yes | `docs/CHECKSUMS_SHA256.txt` (regenerated 2026-11-14) |
| Generated tables and figures | Yes | `data/wp1`–`wp5`, `figures/` (PDF vector + PNG) |
| One-command reproduction | Yes | see below |
| Input-data provenance and licences | Partial | ERA5 via Copernicus CDS; licences per dataset are recorded in `docs/WP1_Parameter_Source_Ledger.md`, not as a single licence file |
| Immutable versioned archive with DOI | **No** | Requires a Zenodo/figshare deposit; cannot be created from this repository alone |

## One-command reproduction

```bash
cd Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript
make check test            # 10/10 config blocks, 8/8 datasets, 35 pytest tests
```

That verifies the package against the shipped artifacts. Full regeneration from raw inputs is:

```bash
python3 scripts/wp1_extract_climate_era5.py          # ERA5 8760 h per site
python3 scripts/wp1_multiyear_climate_robustness.py  # 2014-2023 decade reruns
python3 scripts/wp1_build_optical_nk.py              # dispersive optical constants
python3 scripts/wp1_extract_lhcii_hamiltonians.py    # H1-H3 site energies
python3 scripts/wp1_extract_pdb_dipoles.py           # 1RWT/2BHW dipoles
python3 scripts/wp1_wind_load_screening.py           # M9 site wind screening
python3 scripts/wp2_tmm_opv.py                       # TMM library, Pareto front
python3 scripts/wp2_mesohops_hpc_benchmark.py        # MesoHOPS 1.8.0 benchmark
python3 scripts/wp2b_device_tolerance_audit.py       # M9 fabrication tolerance
python3 scripts/wp2_quantum_ness.py                  # LHCII NESS bounds
python3 scripts/wp3_microclimate_crop_engine.py # hourly crop engine
python3 scripts/wp3b_structural_and_louver_audit.py
python3 scripts/wp5_tea_lca_sobol.py            # TEA, LCA, Sobol
python3 scripts/wp5b_sobol_robustness.py
python3 scripts/wp5c_sobol_convergence.py       # M10 diagnostics
python3 scripts/wp5_export_acceptance_sensitivity.py
python3 scripts/wp6_generate_figures.py
python3 scripts/make_release_manifest.py        # refresh docs/CHECKSUMS_SHA256.txt
```

The WP1 extraction step needs a Copernicus Climate Data Store account; every later step runs from
the shipped `data/wp1` artifacts, so the analyses are reproducible without network access.

## What a deposit still needs (author action)

1. Zenodo (or institutional) deposit of this directory plus the environment lock, with the
   generated `docs/CHECKSUMS_SHA256.txt` as the integrity record.
2. A licence stated in the deposit metadata: the repository root declares MIT for the code, and
   the deposited data need a licence compatible with the ERA5 Copernicus terms of use.
3. The DOI written into the manuscript's Data-availability statement and the cover letter.

Until the DOI exists, the manuscript's data-availability statement points at archived package
artifacts and the repository. It must not be described as an archival release.
