# Deep Recon — Gaps & Novelty, Tri-Crop Extension (Coffee / Pepper / Tea)
Date: 2026-11-12 · Method: BMAD `bmad-deep-recon` · Type: domain + academic-lit · Shape: **select** + **explore**.

---

## 1. Claim Register

| ID | Claim (as retrieved) | Primary Literature & Field Reference | Status |
|---|---|---|---|
| C1 | Coffee-PV: yields increase +40% to +70% for modern F1 hybrids under 30–40% shade; cooling 2–4 °C | CIRAD/IRAD (BREEDCAFS Foumbot), Bertrand et al. 2021 | Verified |
| C2 | Arabica Cameroon: smallholder yields ~850 kg green/ha; farm-gate 2,000–2,800 XAF/kg; organic premium access via cooperative | ONCC reports; ICO database | Verified |
| C3 | **Penja white pepper**: PGI 2013 (first in SSA); Moungo (Littoral); yield 800 kg/ha avg; farm-gate 5,000 XAF/kg; export 14,000 XAF/kg | OAPI / EU PGI dossier; CIRAD phytopathology survey | Verified |
| C4 | **Penja pepper living tutor crisis**: *Spondias mombin* tutors die of *Armillaria/Phytopythium* root rot, causing vine collapse; engineered trellises replace diseased tutors while controlling PAR | CIRAD/IRAD pathology reports (2020–2024); OAPI Penja specifications | Verified |
| C5 | **Highland Tea (*Camellia sinensis*)**: Low canopy (1.0 m plucking table); midday PAR moderation alleviates photoinhibition (+9% to +15% fresh leaf yield); promotes theanine accumulation | MDPI / OpenEI tea agrivoltaics field data; Djuttitsa/Ndu estate metrics | Verified |
| C6 | Perennial tropical cash crops in SSA: severe lack of long-term perennial-crop AV data, smallholder-scale mismatch | IIASA / CGIAR / IRENA 2023 | Verified — supports G1′ |
| C7 | Coupled spectral-OPV ↔ crop model ↔ TEA ↔ LCA ↔ Monte Carlo is the state-of-the-art methodology | Applied Energy, Nature Sustainability, Cell Reports Physical Science | Verified |
| C8 | OPV outdoor lifetime: ALD multi-barrier encapsulation achieves $T_{80} \approx 5\ \text{years}$; periodic replacement modeled explicitly | ISOS standards; Chemical Society Reviews | Verified |
| C9 | Quantum coherence in higher plants: solar excitation creates a CW incoherent NESS (Brumer/Kassal/Mančal); Novoderezhkin (2011) uses Modified Redfield–Förster ($15\ \text{cm}^{-1}$ cutoff) on 14-site LHCII; RuBisCO carboxylation ($k_{\text{cat}}\sim 2\text{--}5\ \text{s}^{-1}$) caps $A_v$ | Brumer & Shapiro 2012 (*PNAS*); Kassal et al. 2013; Novoderezhkin et al. 2011 (*PCCP*) | Verified (methodology) — exact canopy $g_c$ computed in WP2/WP4 |
| C10 | Processing electricity demand: modern tea factory ~250–500 kWh_el/t (median 380; older estates up to 600 kWh_el/t, ~45% overnight withering + ~4,500 kWh_th/t drying heat); coffee wet milling ~25 kWh/t (90% day); pepper ~45 kWh/t (85% day) | Energypedia; IIT Delhi / Sri Lanka tea benchmarks | Verified |

---

## 2. Crop Selection & Tri-Crop Synthesis

| Criterion | Arabica Coffee (*Coffea arabica*) | Penja White Pepper (*Piper nigrum*) | Highland Tea (*Camellia sinensis*) |
|---|---|---|---|
| Natural niche | Understory shrub, shade-adapted | Understory tropical liana | Understory evergreen shrub |
| Optimum shade | 25% – 40% | 20% – 35% | 30% – 50% |
| Agro-ecological zone | Western Highlands (Foumbot/Noun, 1 450 m) | Moungo volcanic lowlands (Njombé-Penja, 250 m) | Western/NW Highlands (Djuttitsa/Ndu, 1 850 m) |
| Canopy height | 2.2 m | 3.5 m (trellis) | **1.0 m (plucking table)** |
| Mounting clearance | 2.4 m | 3.8 m | **2.2 m** |
| Baseline yield | $850\ \text{kg/ha}$ (green coffee) | $800\ \text{kg/ha}$ (dry white pepper) | $1\,800\ \text{kg/ha}$ (made tea) |
| Farm-gate price | 2,400 XAF/kg | 5,000 XAF/kg | 1,800 XAF/kg |
| Premium price | 3,100 XAF/kg (organic) | 14,000 XAF/kg (certified PGI export) | 2,600 XAF/kg (high-altitude orthodox) |
| Processing power demand | 25 kWh/t (90% day) | 45 kWh/t (85% day) | **380 kWh_el/t median [250–600] (55% day / 45% overnight withering)** |
| Role in manuscript | Primary agroforestry baseline | High-value gourmet spice / tutor replacement | Low-CAPEX canopy / captive industrial load |

---

## 3. Refined Gaps & Novelty

| Gap | Description | Claim in This Paper |
|---|---|---|
| **G1′** | Spectrum-resolved ST-OPV (ePAR, R:FR, diffuse sky) + LWIR microclimate co-design over perennial tropical crops remains untested in open fields (Chinese PV-tea trials use poly-Si; Brazil/India cover agroforestry or vines) | **Crop-dependence atlas**: optimal transmittance, LWIR-aware microclimate cooling, and 4-lever yield attribution for coffee, pepper, and tea |
| **G2′** | Quantum-agrivoltaic claims confuse pulsed lasers with CW sunlight and lack a computed scale bound | **CW NESS LHCII–FVCB bound** ($g_c$ computed via Modified Redfield–Förster + targeted MesoHOPS v1.8.0 benchmark across $A_j$ and $A_v$ regimes) |
| **G3′** | Agrivoltaic TEA ignores tropical OPV $T_{80}$ degradation and relies on carbon credits | **Lifetime-explicit DCF** with 5-year replacement cycles; NEB and NPV reported with and without carbon revenue |
| **G4** | PV output valued at grid price rather than local industrial processing demand | **Captive diesel displacement**: matching PV generation to tea factory withering/drying and coffee/pepper post-harvest processing |
| **G5** | Quality and GI premiums ignored in agrivoltaic financial models | **Stochastic valuation of quality** (PGI pepper export, theanine enhancement in tea, organic coffee premium) |
| **G6** | ST-OPV vs. mature c-Si agrivoltaics rarely benchmarked under identical tropical climates | **2D Technological Regime Boundary**: phase diagrams delineating exact $(T_{80}, C_{\text{mod}}, \text{VPD}, f_{\text{diff}})$ regions where ST-OPV defeats spaced opaque c-Si |
