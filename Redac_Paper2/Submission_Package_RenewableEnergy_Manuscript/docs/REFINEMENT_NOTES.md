# Refinement notes (RE_main_2611.tex, RE_SM_2611.tex)

Files keep the original names so `\externaldocument` (xr) still links main <-> SM.
Red `[AUTHOR CHECK: ...]` notes mark items that need data or a decision from you.
Set `\draftnotesfalse` (preamble, both files) to hide them. 19 notes in total (11 main, 8 SM).

## Applied in the text
- Title: "Sub-Saharan" -> Cameroonian; states the three contributions (shade response, techno-economics, quantum bound). Same title in SM.
- Abstract rewritten: model-based caveat first; 2023 vs decade for pepper (7/10 years, mean +1.85 %); both quantum bounds (3.4e-5 and 2.1e-3); priors stated; no Sobol index in abstract.
- Quantum section: HEOM gap (2.1e-3) is now the conservative envelope; "strictly bounded" removed from Fig. 6 caption; Sobol index no longer sold as "seven orders of magnitude" - replaced by direct comparison (<=3.4e-3 % / 0.21 % vs ~10 %).
- Model-structure caveat (spectral lever acts via photon quantity only), assimilation-as-yield-proxy note, uniform-prior note, third limitations paragraph (ERA5 unvalidated, no shade-yield validation, export-dominated NPV, off-grid is a stress test, 2023 on favourable side).
- T80* = 31.27 yr (coffee) flagged as beyond horizon and tested range.
- Overclaims softened (overturns, retire, rigorously decouples, establishing, fundamentally, cleanly, "should pivot"); "carbon assimilation" -> CO2.
- Conclusions: pepper qualified (7/10 years); final sentence conditional.
- Sections 3.5-3.7 (weather years, export acceptance, decision rules, Table 6) moved from Results to the start of the Discussion; labels unchanged. 5.1 retitled "Conditional criteria...".
- Sobol indices rounded to 2 decimals in prose; machine-precision residual text demoted.
- Added Funding section, data-availability DOI note, AI-declaration check.
- SM: HEOM observable note, "vanish" -> "bounded", prior caveat, new section S8 + table of economic inputs (documented values filled; undocumented ones flagged).

## NOT done (needs new analysis or figure regeneration)
1. Numeric export tariff, source, FX, inflation, O&M, degradation (flagged in SM economic-inputs table).
2. NPV decomposition + ground-mounted PV-only comparator; LER definition; hectare normalisation.
3. Energy-matched c-Si scenario (GCR 30-35 %) with crop yield.
4. ERA5 validation vs satellite/station data; spectral (R:FR) sensitivity; load-matched off-grid case.
5. Condensing the quantum material (Sec. 2.5, Sec. 4, SM S2) - editorial decision.
6. Renaming scenarios S0-S6 (collide with SM sections S1-S7) - requires regenerating figures/tables.
7. Fig. 1a legend still says "Focal WP3/WP5 stacks" (image file).
8. Trimming repeated headline numbers across abstract/results/discussion/conclusions.

## Inconsistencies to resolve against the data (not guessable from the text)
- Carbon-price S_Ti: 0.0011 (Results) vs 0.0052 (Discussion).
- k_RC sweep bound: 1.94e-5 (manuscript) vs 1.181e-5 (data report).
- Pepper OPV-cSi inter-year SD: 0.30 pp (data report) vs 0.06-0.19 pp (SM S7.4).
- Table S7 coffee decade maximum (-6.38) equals the 2023 c-Si coffee value.
- Data report: exec summary says tea wet -8.6 % / pepper 0.0 % vs Table 3 (-8.84 / +0.04, -1.36); S5 louver range 357.7-717.2k (report) vs 357,696-826,855 (SM); report Sec. 6 figure order differs from the manuscript.

## Validation performed
Compiled with a stand-in for elsarticle.cls (not installed here) and blank placeholder figures: 0 errors, 0 undefined references (main and SM cross-references resolve). A final compile with elsarticle, your figures and references.bib is still needed.

## Second round (French audit document)
Applied: pepper explicitly "weather-conditional" in Sec. 3.2 and in the Introduction (7/10 years); justification of shade parity vs energy parity (Discussion 5.2); bankability/offtake and policy-lever sentence tied to Table 6 (tab:decision_map); bridge to the companion JPCL study at the start of Sec. 4; "causal" replaced by "attribution" (main Sec. 2.4, SM S3); SM S7.3: hourly means smooth convective gusts, design under national annex.
Adapted, not copied: "Modeled Phenology" was NOT used (the model does not resolve phenology, see limitations); the claim that 25-30 m/s gusts are "common" is not supported by the data provided, so no number was added; policy wording is conditional (T80 >= 16.3 yr applies to pepper only; coffee parity is unattainable in the tested range).
Still outside the .tex: Fig. 3a panel title ("Causal Attribution") is inside the image and must be regenerated; graphical abstract and ORCID iDs are separate submission items.
Prose words (same estimator): original ~4,630 -> now ~5,380, inside the 4,000-6,000 target; re-count with the journal's tool after the red notes are removed.
Compile check (stand-in class, your references.bib): 0 errors, 0 undefined references/citations.
