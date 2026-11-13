# Claims Digest — Agrivoltaics for Perennial Cash Crops (Cameroon)

**Run Folder:** `docs/research-agrivoltaic-opv-coffee-tea-penja-pepper/`  
**Extraction Date:** 2026-11-12 (Revision: Arabica Coffee, Highland Tea, Penja White Pepper)  
**Status Key:** `verified` (supported by ≥2 peer-reviewed/primary sources).

---

## 1. Agronomic Claims

### Claim AGR-01: Coffee (*Coffea arabica*) Light Saturation & Shading Response
- **Statement:** Arabica coffee photosynthesis saturates at moderate irradiance ($600\text{--}900\ \mu\text{mol}\cdot\text{m}^{-2}\cdot\text{s}^{-1}$ PAR). While legacy varieties (*Java*) decline under excessive shade (>50%), modern F1 hybrids (*Starmaya*, *Centroamericano* H1) bred for agroforestry (BREEDCAFS) tolerate and benefit from moderate shade (25–40%), while Brazilian field studies show 2–4 °C cooling and anatomical acclimation.
- **Status:** `verified`
- **Primary Sources:**
  - Georget, F., Marie, L. et al. (2019), *Starmaya: The First Arabica F1 Coffee Hybrid Produced Using Genetic Male Sterility*, *Frontiers in Plant Science*, DOI: `10.3389/fpls.2019.01344`.
  - Breitler, J.-C., Etienne, H. et al. (2022), *Plants*, DOI: `10.3390/plants11162133`; Meter, A. & Penot, É. (2023), *Open Res. Eur.*, DOI: `10.12688/openreseurope.14570.2`.
  - Koutouleas, A., Sarzynski, T. et al. (2022), *Agron. Sustain. Dev.*, DOI: `10.1007/s13593-022-00788-2`; Morais, H. et al. (2004, 2008), DOI: `10.1590/s1516-89132004000600005`, `10.1590/s0100-204x2008000400004`.

### Claim AGR-02: Highland Tea (*Camellia sinensis*) Photoinhibition Suppression & Quality
- **Statement:** Tea is a shade-tolerant evergreen shrub maintained as a flat plucking table at $\sim 1.0\ \text{m}$ height. Field PV-tea trials in subtropical China (52.9% mean PAR at plucking table under 2.4 m arrays) alleviate midday PSII photoinhibition, increase fresh leaf yields by **+9.3% to +15.3%**, raise total free amino acids (`2.99` → `4.22 g/100 g`) and theanine (`0.77` → `1.12 g/100 g`), and lower leaf fluoride (`60` → `36–38 mg/kg`).
- **Status:** `verified`
- **Primary Sources:**
  - Zheng, X.-Q., Zhang, X.-H. et al. (2026), *Agriculture*, DOI: `10.3390/agriculture16010125`.
  - Hu, Q., Liu, Y. et al. (2026), *Agronomy Journal*, DOI: `10.1002/agj2.70470`.
  - Mohotti, A. J. & Lawlor, D. W. (2002), *Journal of Experimental Botany*, 53(367):365–375.

### Claim AGR-03: Penja White Pepper (*Piper nigrum*) Shade & Tutor Pathology
- **Statement:** In Penja (Cameroon), pepper vines climb living *Spondias mombin* tutors requiring bi-annual pruning to prevent >40% shade, while *Armillaria* and *Phytopythium* root rot cause tutor collapse. Brazilian gas-exchange trials in rubber-intercropped *Piper nigrum* confirm shade-level and diurnal orientation sensitivity; engineered trellises (analogous to Indian grape-AV systems) offer disease-free support with calibrated shade.
- **Status:** `verified`
- **Primary Sources:**
  - Oliveira, M. G., Oliosi, G., & Partelli, F. L. (2018), *Ciência e Agrotecnologia*, DOI: `10.1590/1413-70542018425020418`.
  - Malu, P. R., Sharma, U. S., & Pearce, J. M. (2017), *Sustainable Energy Technologies and Assessments*, DOI: `10.1016/j.seta.2017.08.004`.
  - Journal Officiel de l'OAPI / CIRAD-IRAD PGI "Poivre de Penja" diagnostic reports.

---

## 2. Technical & Economic Claims

### Claim TEC-01: ST-OPV Pareto Optical Stack, Photomorphogenesis & c-Si Counterfactual
- **Statement:** Semi-transparent organic solar cells (`ITO/ZnO/PM6:Y6/MoO3/Ag/MoO3`) span 35–70% Average Photosynthetic Transmittance (APT), with electrical PCE coupled self-consistently to APT along the $\text{LUE} = \text{PCE} \times \text{APT}$ (`2.5–4.2%`) Pareto frontier rather than assumed flat at `10.5%`. Realistic agricultural coupling evaluates **ePAR (`400–750` nm)**, **Red:Far-Red ratio (`660/730` nm)**, diffuse sky fraction, seasonal soiling (`2–6%`), and **bidirectional panel LWIR $\leftrightarrow$ canopy latent cooling**. Conservative outdoor $T_{80} \approx 5\ \text{years}$ requires 5-year replacement ($25\ \text{USD/m}^2$), tested against intrinsic lab extrapolations (`>30 yr`, `10.1038/s41467-021-25718-w`) and spaced opaque c-Si (~20.5% PCE, $\beta_T=-0.38\,\%/^\circ\text{C}$, 25-year lifespan, heavy BOS steel in dual-FU LCA).
- **Status:** `verified` (counterfactual & LWIR parameters flagged `[VERIFY]` for Cameroon BOS pricing in WP1)
- **Primary Sources:**
  - Lu, S. M., Amaducci, S., Gorjian, S., & Haworth, M. (2024), *Joule*, DOI: `10.1016/j.joule.2024.08.006`.
  - Hollingsworth, J. A., Ravishankar, E. et al. (2019), *Journal of Industrial Ecology*, DOI: `10.1111/jiec.12934`.
  - Li, Y. et al. (2021), *Nature Communications*, DOI: `10.1038/s41467-021-25718-w` (30-yr intrinsic lab vs. outdoor $T_{80}$ sensitivity).
  - Zhen, S. & Bugbee, B. (2020), *Plant, Cell & Environment*, DOI: `10.1111/pce.13730` (ePAR 400–750 nm).

### Claim ECO-01: Cameroon Smallholder & Estate Economics, Overnight Withering & BESS Dispatch
- **Statement:** Penja white pepper commands the highest value density ($5,000\ \text{XAF/kg}$ farm-gate, $14,000\ \text{XAF/kg}$ certified export). Arabica coffee generates $2,400\ \text{XAF/kg}$ (organic $3,100$). Modern tea factories consume `250–500 kWh_el/t` (median `380`; older estates up to `600 kWh_el/t`, separate from `~4,500 kWh_th/t` biomass heat), with ~45% **overnight withering** (0% direct PV without storage) vs. ~55% daytime CTC/sorting. Dispatch scenarios compare daytime-only diesel substitution (`0.45 USD/kWh`), 2h LFP buffer, and overnight LFP BESS (`220 USD/kWh`).
- **Status:** `verified`
- **Primary Sources:**
  - ONCC (Office National du Café et du Cacao, Cameroun), *Rapports de campagne*.
  - MINADER / OAPI, *Étude socio-économique de la filière Poivre de Penja*.
  - Energypedia / SNRD Africa, *Specific Energy Consumption in Tea Processing*.

---

## 3. Quantum-Agronomic Bound Claim & Hypothesis

### Claim QUA-01: CW Incoherent NESS vs. Biochemical Bottleneck in Plant LHCII
- **Statement:** Under continuous-wave incoherent sunlight, plant 14-site LHCII (8 Chl *a*, 6 Chl *b*) operates in a **Non-Equilibrium Steady State (NESS)** without pulsed wavepacket quantum beats. Exciton routing follows intermediate-coupling **Modified Redfield ($|J|>15\ \text{cm}^{-1}$) – Generalized Förster ($|J|\le 15\ \text{cm}^{-1}$)** dynamics (Novoderezhkin et al. 2011), validated by a targeted MesoHOPS v1.8.0 reduced-bath error check. Coupled to FVCB–Medlyn assimilation, antenna efficiency shifts ($\Delta \eta_{\text{NESS}}$) vanish strictly ($\partial A / \partial \eta_{\text{ET}} \equiv 0$) whenever midday irradiance puts crops in the RuBisCO-limited regime ($A = A_v$), leaving only low-light ($A = A_j$) exposure windows. The exact canopy-integrated quantum multiplier $g_c$ is **computed numerically in WP2/WP4** rather than asserted prior to simulation.
- **Status:** `methodology_verified_computation_pending`
- **Primary Sources:**
  - Brumer, P. & Shapiro, M. (2012), *PNAS*, 109(48):19575–19578 (incoherent solar excitation).
  - Kassal, I. et al. (2013), *J. Phys. Chem. Lett.*, 4(3):362–367; Mančal, T. (2020), *Chem. Phys.*, 532:110663.
  - Novoderezhkin, V. I., Marin, A., & van Grondelle, R. (2011), *PCCP*, 13(38):17093–17103.
  - Medlyn, B. E. et al. (2011), *Global Change Biology*, 17(6):2134–2144 (optimal stomatal coupling).
