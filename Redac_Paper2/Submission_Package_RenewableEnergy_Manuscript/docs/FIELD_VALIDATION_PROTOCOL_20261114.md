# Pre-registered paired field validation protocol (M8)

**Status:** design document, **no data collected**, no validation result claimed. This file exists so
that the protocol is fixed before any measurement, as mitigation item **M8** requires.
**Prepared:** 2026-11-14 · **Package:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`
**Model under test:** `RE_main_2611.tex` with `parameters.yaml` (`framework_version: 2.5.0`)

## 1. What is being tested, and what is not

The manuscript reports four modelled contrasts. Each becomes one pre-specified estimand, with its
own unit and its own decision rule; none is pooled into a single ranking.

| ID | Estimand | Unit | Modelled value (2023 baseline) |
|---|---|---|---|
| E1 | ST-OPV − c-Si marketable yield **at matched crop light** | percentage points | coffee −0.70, pepper +0.48, tea −1.05 |
| E2 | Shade effect on yield (each PV arm − open sun) | percentage points, annual and seasonal | dry +8.8 to +30.2; annual coffee −7.08, tea −3.35, pepper +7.43 |
| E3 | Spectral-selectivity effect, i.e. E1 with shade fraction held the same in both arms | percentage points | ≤ 1.05, with spectral lever −0.21 to −0.67 |
| E4 | Array yield and dispatch (energy, not agronomy) | kWh per installed kWp; LSF | 1044–1223 MWh/ha/yr; LSF 88.6–99.9 % |

E1–E3 are agronomic; E4 is electrical. The protocol requires them to be reported separately
because they are not commensurable, which is the same reason the manuscript refuses a single
"outperforms" statement.

**Explicitly out of scope:** the quantum-channel conclusion (E5). No field trial can resolve a
3 × 10⁻⁵ efficiency shift; the quantum result is a solver-level bound and must not be listed as a
field-testable endpoint. Writing it into a trial protocol would be a category error.

## 2. Design

**Four arms per site, paired within blocks.**

1. `S0` open sun (unshaded control)
2. `S1` traditional shade tree (existing agroforestry reference)
3. `S2*` elevated c-Si **shade-matched** to the ST-OPV arm (GCR ≈ 40 % in the model)
4. `S3` ST-OPV APT44 at GCR 65 % (focal design)

Arm 3 is not optional. Without a shade-matched c-Si arm the design cannot separate E1 from E3, and
the central claim of the paper — shade fraction governs, spectral selectivity does not — becomes
untestable.

**Blocking:** each block contains one plot of each arm, sited on the same soil map unit, slope class
and row orientation, within a single management unit. Blocks are the replication unit for all
agronomic endpoints. A split-plot arrangement is allowed only if the PV arms must share a
substation; the analysis must then declare block × arm as the error stratum for E1–E3.

**Sites:** Foumbot (arabica coffee, 1044 m), Njombe-Penja (Penja white pepper PGI, 273 m),
Djuttitsa (highland tea, 1400 m). One crop per site; no cross-site pooling of raw yields.

**Duration:** minimum three complete harvest cycles per site, and not fewer than 24 months, so that
one dry season and one monsoon season are each observed at least twice. Perennial crops are
permanent installations, so plots must be established on production stands with a recorded
pre-treatment yield history of ≥ 2 years; that history supplies the baseline covariate.

## 3. Replication: computed, not asserted

The model cannot supply the field variance. The modelled inter-year standard deviation of the
OPV–c–Si contrast is only 0.06–0.19 percentage points because both arms share the same weather, so
a power calculation based on it would return `n = 1` and would be wrong. Replication is therefore
tabled against the **assumed plot-level standard deviation of the paired difference** σ_d, which
must be replaced by the value measured in a pilot season.

Paired design, two-sided α = 0.05, power = 0.80, n = ((1.96 + 0.842)·σ_d/δ)²:

| Detectable difference δ | σ_d = 1 pp | σ_d = 2 pp | σ_d = 3 pp | σ_d = 4 pp |
|---|---|---|---|---|
| 0.5 pp | 31 | 126 | 283 | 502 |
| 1.0 pp | 8 | 31 | 71 | 126 |
| 1.5 pp | 3 | 14 | 31 | 56 |
| 2.0 pp | 2 | 8 | 18 | 31 |

Minimum detectable difference for a realistically affordable design (80 % power):

| Paired plots per arm | MDD at σ_d = 2 pp | MDD at σ_d = 3 pp |
|---|---|---|
| 8 | 1.98 pp | 2.97 pp |
| 12 | 1.62 pp | 2.42 pp |
| 16 | 1.40 pp | 2.10 pp |
| 24 | 1.14 pp | 1.71 pp |

**Consequence that must be stated in any resulting paper.** The modelled E1 contrast is ≤ 1.05
percentage points. At σ_d = 3 pp, a 16-plot design cannot resolve it. A field campaign with fewer
than ~70 paired plots per arm is therefore not a test of E1 at the effect size the model predicts;
it can only test E2 (dry-season shade benefit of +8.8 to +30.2 pp) and the sign of the annual
response. This is the honest reading, and it is the reason the manuscript frames its conclusions as
screening hypotheses rather than predictions.

## 4. Measurements (fixed list, with instrument classes)

| Variable | Instrument class | Cadence |
|---|---|---|
| Incident and below-canopy PAR (400–700 nm) | Quantum sensor pair per plot, cosine-corrected | 1 min logging, hourly means archived |
| Transmitted spectrum | Spectroradiometer, 300–1100 nm, above and below canopy | Monthly clear-sky and overcast campaigns, plus one per phenological stage |
| Leaf temperature | IR thermography (emissivity-corrected) + type-T thermocouples on 6 leaves/plot | 15 min |
| Air temperature, RH, VPD | Shielded aspirated logger, canopy height | 15 min |
| Soil moisture | TDR/FDR at 10, 30, 60 cm, 3 probes/plot | Hourly |
| Gas exchange (A–Ci, light response) | Portable photosynthesis system, 3 leaves/plot | 6 campaigns/year, diurnal curve monthly |
| Phenology | BBCH-scale scoring | Weekly in season |
| Disease incidence | Coffee leaf rust, *Phytophthora* foot rot, blister blight | Biweekly in season |
| Marketable yield | Dry bean (coffee), dry white pepper, made tea; subplot harvest, oven-dry mass | Per harvest |
| Module performance | String-level I–V tracer + reference cell; soiling assessed by transmittance ratio | Monthly I–V, continuous DC monitoring |
| Structure | Wind speed/direction at array height, tilt/deflection gauges | 10 min |

## 5. Analysis plan (fixed before unblinding)

1. **Primary analysis:** linear mixed model per site, `yield ~ arm + baseline_covariate + (1|block)`,
   with Gaussian errors after a declared transformation; paired contrasts E1–E3 reported with 95 %
   confidence intervals on the percentage-point scale.
2. **Multiplicity:** Holm correction within the family {E1, E2, E3}; E4 reported separately and
   uncorrected, since it is not an agronomic test.
3. **Non-additivity check:** if the arm × season interaction is significant, present seasonal
   contrasts rather than an annual mean, because the modelled claim is precisely a seasonal sign
   inversion.
4. **Model comparison:** the process model is to be run *predictively* on the trial's own weather and
   management record **before** the yield data are unblinded. Agreement is reported as bias and
   limits of agreement, not as R².
5. **Exclusions (all pre-specified):** storm or structural damage to a plot; agronomic intervention
   applied to one arm only; sensor failure covering > 10 % of a season's daylight hours; a harvest
   lost to labour action. Every exclusion is logged with reason and date.
6. **Missing data:** no imputation for yield; report the analysed n per contrast. Missing
   environmental series > 10 % are gap-filled only by a stated model and flagged.

## 6. Decision rule

For each site and season:

- **ST-OPV non-inferiority** is declared if the lower 95 % bound of E1 exceeds −1.0 pp (margin fixed
  before the trial, matching the largest modelled E1 magnitude).
- **Shade superiority** is declared if the lower 95 % bound of E2 exceeds 0 pp in the dry season and
  the sign does not reverse beyond −1.0 pp in the monsoon.
- **Spectral selectivity matters** only if E3's interval excludes zero; the model predicts it does
  not, so a zero-crossing E3 is a confirmation, not a failure.
- **No claim** may be built on a site whose analysed n falls below the number implied by §3 for the
  effect size being claimed.

## 7. Pre-registration and archiving

Register the following **before** the first measurement: this file, the site and block map, arm
assignment and randomisation seed, the instrument list, the primary endpoints and margins, the
analysis script skeleton, and the exclusion rules. Deposit on OSF (or an equivalent registry) with a
timestamped DOI, and archive the trial dataset and analysis code alongside the model package
(see `docs/RELEASE_MANIFEST_20261114.md`).

## 8. What this protocol cannot fix

Even fully executed, the design tests the *contrasts under the tested designs*, not the general
claim that semi-transparent agrivoltaics suits tropical perennials. A four-arm design at one GCR per
site does not map the full shade-fraction response, and a single production stand per site does not
sample the soil and management heterogeneity of a cooperative catchment. Those require additional
arms and sites, which is why the manuscript's conclusions are conditioned on the modelled scenarios
rather than stated as deployment guidance.

**Not claimed:** that this protocol has been funded, approved, registered, or started. None of those
steps has been taken, and no field data exist at the three sites.
