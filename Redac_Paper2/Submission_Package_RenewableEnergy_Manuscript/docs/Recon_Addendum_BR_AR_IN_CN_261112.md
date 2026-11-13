# Recon Addendum — Primary Sources from China, Brazil, India & Argentina (2026-11-12)

**Status:** **Primary sources retrieved and verified via OpenAlex API** (`/tmp/oa/out_fast.txt`, `/tmp/oa/out_bcin.txt`). All DOIs, journals, authors, and quantitative abstracts below were read directly from primary OpenAlex metadata.

---

## 1. Verified Primary Literature by Region

### A. China (PV-Tea Field Trials & NFA ST-OPV Lifetime)
1. **Zheng, X.-Q., Zhang, X.-H., Zhang, J.-G., & Zheng, R.-J. (2026)**, *Agriculture*, DOI: [`10.3390/agriculture16010125`](https://doi.org/10.3390/agriculture16010125)  
   *Title:* "Effects of Photovoltaic-Integrated Tea Plantation on Tea Field Productivity and Tea Leaf Quality"  
   *Primary setup & numbers:* Single-axis tracking (±45°, 70×270 Wp poly-Si modules, 4.5 m spacing, **2.4 m mounting height**, 656 kWp/ha). Mean PAR at plucking table = **52.9% of control** (**32.0%** sunny day, **49.0%** cloudy day); higher ambient RH; alleviates midday PSII depression; **+9.3% to +15.3% fresh leaf yield increase**.
2. **Hu, Q., Liu, Y., Fu, H., & Wei, J. (2026)**, *Agronomy Journal*, DOI: [`10.1002/agj2.70470`](https://doi.org/10.1002/agj2.70470)  
   *Title:* "Photovoltaic shading as a cultivation strategy to improve summer–autumn tea quality: Microclimate regulation and biochemical responses across subtropical regions"  
   *Primary numbers:* Tested two subtropical Chinese radiation regimes (60–70% and 80–90% nominal geometric shading). Lower air and leaf temperatures, higher RH, higher SPAD and $\Phi_{\text{PSII}}$. Under high radiation, total free amino acids rose from **2.99 to 4.22 g/100 g**, theanine rose from **0.77 to 1.12 g/100 g**, and fluoride fell from **60 to 36–38 mg/kg**.
3. **Li, Y., Huang, X., Ding, K., Sheriff, H. K. M., et al. (2021)**, *Nature Communications*, DOI: [`10.1038/s41467-021-25718-w`](https://doi.org/10.1038/s41467-021-25718-w)  
   *Title:* "Non-fullerene acceptor organic photovoltaics with intrinsic operational lifetimes over 30 years"  
   *Relevance:* Encapsulated NFA-OPVs with buffer layers + solution-processed UV filter retain 94% PCE after 1,900 h at 1-sun (55 °C) and extrapolate to $>5.6 \times 10^4\ \text{h}$ (~30 yr) *intrinsic* operational stability under controlled filtering — contrasting sharply with unmitigated humid tropical outdoor degradation (`t80_lifetime_years = 5.0` baseline in `parameters.yaml`), justifying scanning $T_{80} \in [3, 25]\ \text{yr}$ in the G6 phase map. Additional Chinese/global reviews: **Jiang & Hu (2022)**, *Chem. Sci.*, [`10.1039/d1sc07269b`](https://doi.org/10.1039/d1sc07269b); **Yu & Li (2025)**, *Polym. Sci. Technol.*, [`10.1021/polymscitech.4c00054`](https://doi.org/10.1021/polymscitech.4c00054).

### B. Brazil (Coffee & Black Pepper Shade Ecophysiology — SciELO / Embrapa / UFLA)
1. **Oliveira, M. G., Oliosi, G., & Partelli, F. L. (2018)**, *Ciência e Agrotecnologia* (UFLA), DOI: [`10.1590/1413-70542018425020418`](https://doi.org/10.1590/1413-70542018425020418)  
   *Title:* "Physiological responses of photosynthesis in black pepper plants under different shade levels promoted by intercropping with rubber trees"  
   *Relevance:* Primary *Piper nigrum* gas-exchange dataset across full sun + 5 shade levels in Brazil, demonstrating diurnal & row-orientation effects on leaf gas exchange.
2. **Morais, H., Medri, M. E., et al. (2004)**, *Braz. Arch. Biol. Technol.*, [`10.1590/s1516-89132004000600005`](https://doi.org/10.1590/s1516-89132004000600005); **Morais, H., Marur, C. J., et al. (2008)**, *Pesquisa Agropecuária Brasileira* (Embrapa), [`10.1590/s0100-204x2008000400004`](https://doi.org/10.1590/s0100-204x2008000400004); **Morais, H., Caramori, P. H., et al. (2009)**, *Ciência Rural*, [`10.1590/s0103-84782009000200013`](https://doi.org/10.1590/s0103-84782009000200013)  
   *Relevance:* Primary Brazilian field benchmarks on shaded *Coffea arabica* leaf anatomy, floral bud initiation, photosynthetic gas exchange, and productivity.
3. **Koutouleas, A., Sarzynski, T., et al. (2022)**, *Agronomy for Sustainable Development*, [`10.1007/s13593-022-00788-2`](https://doi.org/10.1007/s13593-022-00788-2) + Cameroon/BREEDCAFS hybrids **Georget et al. (2019)**, *Front. Plant Sci.*, [`10.3389/fpls.2019.01344`](https://doi.org/10.3389/fpls.2019.01344) (*Starmaya* F1 hybrid) and **Breitler et al. (2022)**, *Plants*, [`10.3390/plants11162133`](https://doi.org/10.3390/plants11162133) (agroforestry coffee ideotype) + **Meter & Penot (2023)**, *Open Res. Eur.*, [`10.12688/openreseurope.14570.2`](https://doi.org/10.12688/openreseurope.14570.2).

### C. India (Agrivoltaics Potential & Tropical Agroforestry Analogues)
1. **Malu, P. R., Sharma, U. S., & Pearce, J. M. (2017)**, *Sustainable Energy Technologies and Assessments*, [`10.1016/j.seta.2017.08.004`](https://doi.org/10.1016/j.seta.2017.08.004) — perennial vine (grape) agrivoltaics in India (trellis analogue to Penja *Piper nigrum*).
2. **Aswal, P., & Sundriyal, N. (2026)**, *Sustainable Energy Research*, [`10.1186/s40807-026-00277-0`](https://doi.org/10.1186/s40807-026-00277-0) & **Sharma & Banerjee (2026)**, [`10.35940/ijies.b1056.13010126`](https://doi.org/10.35940/ijies.b1056.13010126) — Indian land-use agrivoltaic modeling.
3. **Haq, M. Z. U. et al. (2026)**, *Agricultural Systems*, [`10.1016/j.agsy.2026.104924`](https://doi.org/10.1016/j.agsy.2026.104924) — multi-strata tropical agroforestry for spices and beverage understory crops (`LER > 1.0`).

### D. Argentina, East Africa & Spectral-Sharing Benchmarks
1. **Palazzo, L., & Acosta, G. L. (2024)**, *AgriVoltaics Conference Proceedings*, [`10.52825/agripv.v1i.612`](https://doi.org/10.52825/agripv.v1i.612) — *"Towards a More Sustainable Viticulture: Integration of Solar Photovoltaic Projects in Vineyards"* (Argentine trellis/viticulture AV benchmark; inorganic ST-PV over soybean remains secondary/grey outside AgriVoltaics viticulture).
2. **Lu, S. M., Amaducci, S., Gorjian, S., & Haworth, M. (2024)**, *Joule*, [`10.1016/j.joule.2024.08.006`](https://doi.org/10.1016/j.joule.2024.08.006) — authoritative review of wavelength-selective PVs, optimal bandgaps, and crop spectral-sharing standardization.
3. **Randle-Boggis, R. J., Kuria, A. W., Cotton, M., & Parkhill, K. A. (2026)**, *Applied Energy*, [`10.1016/j.apenergy.2026.128450`](https://doi.org/10.1016/j.apenergy.2026.128450) — Kenya & Tanzania TEA: mounting structures = **45% of non-battery CAPEX**, ground-mounted PV 16–27% cheaper, crop income narrows payback gap to 1–3 yr (directly supports our Cameroon BOS sensitivity & tea 1.0 m / 2.2 m low-CAPEX framing).
4. **Zhang, W., & Hendriks, P.-W. (2025)**, *Agron. Sustain. Dev.*, [`10.1007/s13593-025-01060-z`](https://doi.org/10.1007/s13593-025-01060-z) — meta-analysis of climatic and design tipping points in agrivoltaics.

---

## 2. Citation Integrity Audit & Gap Adjustments
1. **Purged two erroneous DOIs discovered during OpenAlex check:**
   - Removed wrong BREEDCAFS DOI `10.3389/fpls.2021.641457` (actually citrus HLB!) → replaced with verified **Georget et al. (2019)** `10.3389/fpls.2019.01344`, **Breitler et al. (2022)** `10.3390/plants11162133`, **Meter & Penot (2023)** `10.12688/openreseurope.14570.2`, and **Koutouleas et al. (2022)** `10.1007/s13593-022-00788-2`.
   - Removed wrong Ravishankar DOI `10.1016/j.xcrp.2022.100781` (actually water spinach WEC2P!) → replaced with verified **Hollingsworth, Ravishankar et al. (2019)** `10.1111/jiec.12934`, **Lu et al. (2024, *Joule*)** `10.1016/j.joule.2024.08.006`, **Loik et al. (2017)** `10.1002/2016ef000531`, and **Li et al. (2021, *Nat. Commun.*)** `10.1038/s41467-021-25718-w`.
2. **Tightened G1′ Gap Wording:** Acknowledges existing field PV-tea trials in China (`10.3390/agriculture16010125`, `10.1002/agj2.70470`) and perennial trellis/agroforestry shade datasets in Brazil (`10.1590/1413-70542018425020418`) and India (`10.1016/j.seta.2017.08.004`). Our distinct open gap is **spectrum-resolved ST-OPV co-design (ePAR, R:FR, panel LWIR, Medlyn $g_s$–VPD) benchmarked head-to-head against spaced c-Si** across Cameroon's three contrasting cash crops and captive rural processing loads.
