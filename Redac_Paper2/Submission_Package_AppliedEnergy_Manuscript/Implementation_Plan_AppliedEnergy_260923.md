# Implementation Plan — Paper 2 → Applied Energy (260923)

Target: Applied Energy (Elsevier, ISSN 0306-2619), research article, initial submission.
Official source: elsevier.com / sciencedirect.com Guide for Authors (direct fetch blocked HTTP 400 anti-bot 2026-09-23; synthesis via indexed official snippets + 2026 relays — RE-VERIFY in Editorial Manager before upload).
Checked: 2026-09-23. Skills: `venue-templates` (format workflow), `scientific-writing` + `peer-review` (claims/questions; applied in prior phase, same rigor).

## 1. Format gap analysis (current → action)

| # | Requirement AE | Current (260923) | Action |
|---|---|---|---|
| F1 | Body ~8000 words max | ~5774 → OK (margin ~2200) | None; do NOT bloat past ~7000 |
| F2 | Abstract ≤200 (safe) | 133 → OK | None |
| F3 | Highlights 3–5 × ≤85ch, separate file | 5 × 69–74ch → OK | None |
| F4 | Keywords 4–6 | 6 → OK | None |
| F5 | CRediT statement | ABSENT | ADD (P0) |
| F6 | Competing interests declaration | ABSENT | ADD (P0) |
| F7 | Funding statement | ABSENT | ADD (P0, even if none) |
| F8 | GenAI declaration | ABSENT | ADD (P0, or "none used") |
| F9 | Nomenclature | ABSENT (many symbols Φ, g0, ETc…) | ADD (P0) |
| F10 | Graphical abstract ≥531×1328 px wide | DONE 26-09-23: `figures/Graphical_Abstract_wide.png` 2048×1024 (fixed 1024² square + navy text panel, title + 3 bullets) + `figures/Graphical_Abstract_fixed.png` (AI-garbled labels repaired: Red/Green/Au/Au, verified native 1:1) | DONE |
| F11 | ORCID authors | ABSENT | ADD (P1) |
| F12 | `table_comparative_4runs.tex` orphan (not `\input`) | NOT orphan: `\input` in SI.tex L757 → KEEP, no action | Decided (P1) — DONE |

## 2. Central question (old → new)

OLD (Nature-Energy style): "convert the food-energy conflict into synergy via OPV spectral shaper + NPoM sentinel + shield + twin."
Problem: promise of synergy, hype framing, undersells the method.

NEW (proposed, to place end of Intro + mirror in abstract/conclusion):
> "Can exact non-Markovian quantum dynamics (PT-HOPS) jointly optimize excitation-transport efficiency and power-conversion efficiency in a sensing-integrated photothermal agrivoltaic stack — and does the multifunctional net energy benefit (heat + power + crop + sensing, $/W + $/kg + $/m³) stay positive under field constraints?"

Why better: (a) names the method + the joint optimization (ETR+PCE) = the actual novelty (gap G1); (b) makes NEB falsifiable = Applied Energy language; (c) bounds scope to modelled conditions.

## 3. Claims adaptation (hype → engineering-quantified)

| # | Location | Current | Adapted |
|---|---|---|---|
| C1 | Abstract + body | "converting the food-energy conflict into a functional synergy", "symbiotic", "quantum-engineered" | "under modelled conditions, co-design raises X by Y% relative to baseline Z" |
| C2 | Abstract/Disc. | "scalable pathway", "economically transformative" | Scope to 500 m² case + payback/NPV numbers already present |
| C3 | NPoM | "firmly in strong coupling", "numerically exact precision" | Keep numbers (geff~2000 > κ~800), drop adverbs; state convergence (L7→L8 3.1e-11) once |
| C4 | SERS | "single-molecule-sensitivity", "irreplaceable diagnostic" | Report EF/LOD numbers only + matrix penalty already present |
| C5 | Twin/QKD | "real-time virtual replica… closed-loop optimal", "physical sovereignty" | "model-based supervisory twin; fallback 5 L/m²/j" |
| C6 | NPoM-off baseline | "should not be compared" (l235) | Move to SI or reframe as limiting case — reviewer-energy red flag |
| C7 | OPEX | 1.2k+0.8k ≠ 4k total | FIX arithmetic (P0, credibility) |
| C8 | Discussion | QAOA/gravimetry/MPS/QKRR block | Condense to 1 paragraph or move to SI (P1) — too speculative for AE |

## 4. Gaps/novelty enrichment (refs VERIFIED 2026-09-23 via CrossRef/arXiv/OpenAlex; see verification table below)

Claim these 3 open gaps (none found occupied):
- G1. No exact-OQS-guided operating agrivoltaic stack (PT-HOPS/HEOM → ETR+PCE co-design, not post-hoc modelling).
- G2. No monolithic photothermal-heating + PV + SERS-readout device with field calibration in one footprint (DiDomenico2026 review lists no SERS category).
- G3. No NEB-style multifunctional TEA/LCA ($/W + $/kg + $/m³ + minerals) for sensing-integrated agrivoltaics.

Frame around 3 threats (cite + differentiate):
- T1. TeguiaKouam2026 arXiv:2603.04097 (PT-HOPS + OPV filter + ETR/SPCE/$) — declare as own-precursor chain (Paper 1 JPCL jz-2026-00994t); Paper 2 adds hardware photothermal + SERS + NEB/LCA.
- T2. TemizDincer2024 Appl. Energy 358 (multi-vector agri + H2 + desal) — differentiate by quantum-guided spectral co-design + integrated sensing; compare $/W + $/kg + $/m³ head-to-head.
- T3. Ravilla2024 / Bellone2024 (Nik Zad co-author, supplants unverifiable Nik Zad 2025 SPC claim) / Kashif 2025 REJECTED (only 2026 SSRN preprint exists — do NOT cite as 2025 article) — adopt their functional-unit discipline; internalise heat + sensing + steel-minerals trade-off.

Insertions (all in references.bib since 2026-09-23): Valle2017 / Amaducci2018 (already present, verified identical — no action); Wu2023Energies (first author Wu, NOT Xiao — photothermal greenhouse precedent, distinguish passive); Lambert2023 QuTiP-BoFiN (nearest HEOM-device use, distinguish no-PV); Zidane2025 (replaces Bdour 2024 $/m³ template — Bdour 2024 REJECTED, no record); DiDomenico2026; Pook2025; Mahim2025; LiuFang2026; Motlagh2024; DuYan2026; So2024 (replaces Pagano 2025 Nat. Commun. — no record — same trapped-ion electron-transfer mechanism); Chopdar 2024 REJECTED (only 2025/26 chapters); Schindele 2020 AE REJECTED as stated (no record; substitute Trommsdorff et al. 2021 RSER if price-performance anchor needed); Anusuya 2024 REJECTED (no record).

### Verification log 2026-09-23
- 16 entries appended to references.bib with exact CrossRef/arXiv metadata (no hand-typed authors/titles); 2 duplicates found and removed (Amaducci2018, Valle2017 already present and correct); bibtex parses with 0 errors (only 3 pre-existing warnings: Nalbach2010, Olson2013, Xu2015).
- 10/16 entries were hand-corrected after a memory-vs-API audit caught guessed author lists (Pook, So, Mahim, Wu, Lambert, Motlagh, DuYan, TeguiaKouam, DiDomenico) — all now match raw API responses.

## 5. Phased plan

**Phase 0 — atomic hygiene (0.5 h):** recompile main+SI+cover after rename; 0 errors/0 undefined gate.
**Phase 1 — compliance P0 (2–3 h):** F5–F10 (CRediT, COI, funding, GenAI, nomenclature, graphical abstract wide) + C7 OPEX fix.
**Phase 2 — questions + claims (3–4 h):** §2 RQ in Intro/abstract/conclusion; Table §3 C1–C6 applied; C8 condense.
**Phase 3 — novelty armor (2–3 h + verification):** verify T1–T3 + foundation cites via CrossRef; insert G1–G3 claim sentences + differentiation paragraphs; F12 decide.
**Phase 4 — gates (1 h):** F11 ORCID; full rebuild; checklist §6.

Total: ~9–12 h. Order: 0 → 1 → 2 → 3 → 4. Do NOT start Phase 3 before 1–2 (citations must land on final prose).

## 6. Verification gates

- [ ] Rename 260923 propagated (cover, SI xr, README) — DONE 2026-09-23
- [ ] Elsevier guide re-verified in Editorial Manager at upload
- [ ] Body ≤7000 words, abstract ≤200, highlights re-checked ≤85ch
- [ ] CRediT + COI + funding + GenAI + nomenclature + ORCID present
- [ ] Graphical abstract wide ≥531×1328
- [ ] 0 `\cite` undefined, 0 `??`, compile 0 errors (main + SI + cover)
- [ ] OPEX arithmetic exact; NPoM-off baseline reframed
- [x] All new refs DOI-verified (no TO VERIFY left in bib) — DONE 2026-09-23 (16 in bib, 7 rejected, see §4 log)
- [x] Cover letter mentions prior Nature Energy consideration + subscription route — DONE 2026-09-23

## 7. Application log 2026-09-23 ("go": §1–§3 + §4 insertions applied)

- OPEX "bug" was NOT a bug: SI L426 lists 3 streams (1200+800+2000 maintenance = 4000); main omitted the 3rd stream → fixed by adding it (no number cascade).
- Applied ~30 edits: RQ inserted end of Intro (§2 verbatim, falsifiable); Conclusions section added (AE requires it; mirrors RQ + bounds); CRediT + COI + funding + GenAI + Nomenclature added (CRediT/COI roles flagged `% AUTHOR: confirm`); claims C1–C6 softened (modelled/conditional wording); QAOA/gravimetry framed prospective (full condense deferred); Fig3c caption de-hyped.
- §4 cites inserted (16/16 resolve in .bbl): foundations Valle2017/Amaducci2018/Mahim2025 (Intro), Wu2023Energies (shield, distinguished passive), Lambert2023 + LiuFang2026 + Motlagh2024 (OQS context), DiDomenico2026 (SERS gap G2), Zidane2025 (socio-éco), So2024 (mechanism), Pook2025 + DuYan2026 (twin), TeguiaKouam2026 (own-precursor chain), TemizDincer2024 + Ravilla2024 + Bellone2024 (threats + G1/G3 sentences in prior-art paragraph).
- Cover: prior-Nature-Energy sentence added (transfer declined → direct AE submission).
- Gates now passing: 0 errors, 0 undefined (main), abstract 143w, body ~6080w (<7000), 16/16 new cites in .bbl.
- OPEN (author/data needed): F10 graphical abstract wide (needs image work); F11 ORCID (TODO comment in tex); trajectory-count tension L235 (V=0.8 n=100) vs Tab. caption (non-1.2 entries n=2) — needs output check; QAOA full condense deferred; Editorial Manager re-verify at upload.

## 8. Application log 2026-09-23 (3 restants: F11, L235, QAOA)

- **F11 ORCID — BLOCKED author input.** `% TODO(author, F11)` at tex L75 stands; no ORCID numbers found anywhere in Redac_Paper1/2 (grep `0000-0` = 0 hits). Real IDs must come from the authors — nothing fabricable. Gate stays open.
- **L235-vs-caption — CLOSED (wording), outputs-flagged (numbers).** Caption ↔ body ↔ table verified mutually consistent (1.2nm³: n=20, 0.0799±0.0005; other table entries n=2; V=0.8nm³ extra n=100 run; NPoM-off n=100 limiting-case; Table value 0.0799). 1-word-class fix applied: caption now reads "remaining table entries use n=2 (an additional n=100 run at 0.8nm³ is discussed in the text)". The ±0.0005 error bar itself needs output files to confirm — flagged, not changed.
- **QAOA — CONDENSED.** L349 gravimetry/gradiometer/geodesy detail (~6 lines) → 2-sentence prospective pointer to SI-sec:gravimetry; QAOA formulation + 12–18% gains kept; all 4 cite keys retained. MPS/QKRR paragraph untouched (carries SERS-pipeline numbers).
- **Build:** 0 errors, 0 undefined, 34 pp. **Pre-existing condition found:** 19 overfulls spread L115–485, proven NOT mine (BASE-vs-MINE rebuild comparison: 19 = 19 at identical lines). Offered as next step, out of scope of the 3 items.
- OPEN now: F10 graphical abstract wide; F11 ORCID numbers (authors); ±0.0005 + trajectory outputs; 19 overfulls (pre-existing); Editorial Manager re-verify at upload.

## 9. Application log 2026-09-23 (19 overfulls → 0)

- **Baseline:** 19 overfulls (2 vbox 28.9pt at page-1 shipout + 17 hbox), proven pre-existing (BASE-vs-MINE identical lines).
- **Fixes (4, zéro contenu changé) :** `\sisetup += allow-number-unit-breaks=true` ; `\emergencystretch=2.5em` (preamble, ponytail comment) ; FMO `table*` → `\small` + `\tabcolsep 4pt` ; Nomenclature → `\small` + second column `p{0.68\linewidth}`. Rebuild: 19 → 2 (17 hbox gone).
- **Last 2 vbox (frontmatter page 1) :** `\enlargethispage{32pt}` after `\end{frontmatter}` → 2 → 1. Diagnostic décisif : rebuild sans `\linenumbers` (copie /tmp) = 0 overfull → interaction lineno × footnote auteur. Fix standard : `\nolinenumbers` après `\begin{document}`, `\linenumbers` réactivé après `\end{frontmatter}` (frontmatter non numéroté, corps numéroté — vérifié p.3 : lignes 39–43 présentes).
- **Final : 0 errors, 0 overfull, 0 undefined, 34 pp.** Frontmatter complet p.1 (titre + auteurs + abstract + keywords), intro suit en flux.
- OPEN inchangé : F10 graphical abstract wide ; F11 ORCID (auteurs) ; outputs (±0.0005, trajectoires) ; Editorial Manager re-verify at upload.

## 10. Application log 2026-09-23 (F10 graphical abstract — DONE)

- **Repair (labels, PIL + opencv inpaint, DejaVu Bold) :** `Ploted`→`Red` CLEAN ; `Ald`→`Au` + `Ad`→`Au` (NPoM = Au NP + graphene spacer + Au mirror, per manuscript) CLEAN, no visible patch ; `pretes`→`Green` needed 2 passes (white rotated strip for main chunk + inpaint for pale-green-bg tail x103–132 y300–335) ; native 1:1 check crisp, no ghost/smear.
- **Wide canvas :** `figures/Graphical_Abstract_wide.png` 2048×1024 (fixed square left + navy right panel: title + 3 wrapped headline bullets — payback 4.23 yr, 0.89(3), +25% ETR, NEB 19.6 — + footer) ; v1 overflowed → v2 pixel-measured wrapping, visually verified. `figures/Graphical_Abstract_fixed.png` = repaired square. Original `Graphical_Abstract.png` untouched. README L19 updated.
- OPEN now : F11 ORCID (auteurs) ; outputs (±0.0005, trajectoires) ; Editorial Manager re-verify at upload.

## 11. Application log 2026-09-23 (refinements R2–R15 — DONE sauf R1/R3 auteur)

- **R2 (bib dup keys) — CLOSED, no true duplicates.** 5 flagged keys each defined once; .bbl 63 unique \bibitem, .aux 63 unique \bibcite, single \bibliography (L543–544). 23 natbib "multiply defined" warnings = multi-pass noise (aux re-read at last-page shipout; 0 rerun-needed; output verified correct). No bib change needed.
- **R9/R11/R12 (adoucissements) — DONE.** L375 severe→strong ; L338 link-budget qualifier (QBER grows with distance) ; L289/L290 LODs "under controlled conditions".
- **R8 (sensibilité éco) — DONE.** Sentence after L327, arithmetic verified: net CAPEX ±20% → 3.39–5.08 yr ; OPEX 6000 → 4.58 yr ; revenue −20% → 5.50 yr.
- **R4/R5/R6/R10/R13/R14/R15 (verify-only) — CONFIRMED.** n=2 honesty (L215/L249 + comparison limitation) ; QAOA prospective + gains attributed ; 0 overfulls current log ; 4-domain reviewer slate kept (Olaya-Castro/Yuen-Zhou/Baumberg/Barron-Gafford) ; captions self-contained ; R7 validation paragraphs (Outlook 2DES/field-trials, GQAS, in-situ readout) present.
- **Build : 0 errors, 0 undefined, 0 overfull, 34 pp.**
- OPEN (auteur) : R1 data deposit (Zenodo DOI) ; R3 ORCID. Sinon : outputs, Editorial Manager re-verify at upload.

## 12. Audit journal 2026-09-23 (audit Buffy — cohérence numérique + polish final)

**Décisions auteur (arbitrage) :** gain de rendement = 15 % (pas 8 %) ; 650 m³/yr dérivé du crédit d'eau 1300 L/m²/yr (pas du ΔETc brut).

**Cross-checks PASSÉS :** 0 erreur / 0 undefined / 0 overfull (main 34 pp, SI 24 pp, cover 4 pp) ; bibtex 0 warnings (main+SI) ; abstract 149 mots ≤ 200 ; 6 keywords ; highlights 5×69–74 ch ≤ 85 ; corps ≈ 6100–6800 mots < 7000 ; tous les `\Cref{SI-sec:…}` résolvent (xr bidirectionnel OK) ; ordre figures = ordre de citation.

**Corrections appliquées (toutes vérifiées contre le code source) :**
- **8 % → 15 % (SI S9 + main POC).** Chaîne rétablie : 15 % × 8.2 kg = 1.23 kg/m²/yr → 5.5 $/m²/yr → revenu 30 612 $ → payback 4.23 yr. Cohérente avec SI S5 « 15 % → 5.5 $ ».
- **650 m³/yr redérivé (main POC + SI S9).** Énoncé = crédit d'eau 1300 L/m²/yr (650 m³/yr pour 500 m²), distingué du ΔETc brut (1.3 mm/j ≈ 475 m³/yr). Gravimétrie inchangée (utilise 650 m³/yr sans double origine).
- **Eq. (3) : préfacteur 2 ajouté.** Vérifié code : `src/orchestrator.py` L472 `cumulative_yield = 2.0 * gamma_rc * cumsum(trapped_pop) * dt` (idem `src/digital_twin.py` L109) ; s'aligne sur l'Eq. SI S1 (facteur 2 déjà énoncé). Une phrase de justification ajoutée au main.
- **η_shield = 0.85 corrigé (main L305 + SI thermal shielding).** Vérifié code : `src/iot_security/sensing.py` L174 `effective_delta_t = raw_delta_t * (1.0 - shielding_factor)` ⇒ drift ∝ (1−η). Formules main + SI réécrites avec (1−η) ; 5.25 % → 0.79 % = résidu 15 % explicité.
- **Baseline NPoM-off honnêteté (table_comparative_4runs + SI trace paragraph).** Colonne n_traj=20 désormais étiquetée « limiting case » (caption + note de légende) ; paragraphe trace-conservation du SI réécrit : snapshot exploratoire, valeurs indicatives, baseline complète = run dédié du main.
- **Facteur 2.1 ↔ +45 % à 77 K (SI S8).** 2.1 = rapport des Φ_FT (0.0799→0.1685) à volume égal ; +45 % = population piégée pic (0.0038→0.0055 ; 44.7 arrondi 45). Les deux énoncés distingués.
- **Cover letter :** 79–83 % → 79–84 % (pops plasmon finales 0.7901/0.8256/0.8401) ; enclos Graphical_Abstract.png → Graphical_Abstract_wide.png (F10) ; `\sloppy` ajouté (2 overfull préexistants → 0).
- **Polish SI :** tags de panneaux « (S2 a)/(S2h) » → « (Fig. S2a)/(Fig. S2h) » ; cross-ref distribution ↔ table comparative ; commentaire « FOUR » → « EIGHT » ; 44.7 % → 45 % ; « aligns perfectly » ×2 → « is well matched » ; main : « Site 8 ~ » → « Site 8, ~ » ; « dual OPEX/dual-OPEX » → « OPEX/cooperative OPEX » ; « 1-ha tomato » → « utility-scale tomato scenario » ; EF_SERS « up to 10² » → « EF=44, jusqu'à 1.6×10³ » (aligné Tab. 2).
- **n=100 @ 0.8 nm³ intégré au corps du main** (phrase après la discussion du scan, renvoi SI-sec:comparative_hdf5, plasmon 0.79 / Φ 0.0768) — ferme le flag de tension des comptes de trajectoires (§7).
- **Note artefact trace de la légende Fig. 1 conservée** (décision : le renvoi `\Cref{SI-sec:cryo}` reste utile ; la note vise les runs Δt=10 fs d'intégration, sans ambiguïté sur les résultats de production).

**Build final : 0 erreur, 0 undefined, 0 overfull — main 34 pp, SI 24 pp, cover 4 pp.**

**OPEN (auteur) :** F11 ORCID ; R1 dépôt de données (DOI Zenodo) ; re-vérification outputs (barre ±0.0005, comptes de trajectoires) ; re-vérification guide Editorial Manager à l'upload.

## 13. Application log 2026-09-23 (purge tomate + intégration QST)

**Décisions auteur :** scénario 100 % horticulture (suppression du benchmark « tomate 8.0 yr ») ; intégration des éléments différenciants du package QST.

**Purge « tomate 8.0 yr » (3 occurrences) :**
- Main L329 (§ socio-éco) : phrase « 1.9× shorter than the 8.0 yr payback … tomato scenario » supprimée → remplacée par une synthèse des sensibilités (déjà chiffrées : ±20 % CAPEX, OPEX+50 %, revenu −20 %).
- Main L404 (Methods POC) : « shifts from an 8.0 yr individual payback … » supprimé → remplacé par la chaîne documentée 6.05 yr (subvention) → 4.23 yr + exposition par membre 22 540 $ (= 112 700/5, SI S5).
- SI S9 (smallholder applicability) : même remplacement, avec renvoi \Cref{SI-sec:socioeconomic}.
- Aucune cascade numérique (le 8.0 yr n'était référencé nulle part ailleurs) ; la clé bib de l'article tomate (Scarano2024) n'était pas citée dans le texte — inchangée dans references.bib.

**Intégration QST → AE (option condensée validée) :**
- **Nouvelle sous-section « Experimental testability »** en fin de Results (après BB84) : ~130 mots + **Tableau benchmark expérimental** 6 lignes (J₁₂ −87.7 vs −87.7±5.0 Brixner2005 ; λ_D 35 vs 35–40 Engel2007 ; γ_D 50 Panitchayangkoon2010 ; τ_c 420±35 fs vs 400±50 fs 2DES room T ; g₀ 110 vs 120±15 Chikkaraddy2016 ; EF_SERS 44 vs 10²–10³ Baumberg2019). Chiffres cross-vérifiés cohérents avec AE. Table en colonnes p{} (0.28/0.20/0.44\textwidth) — la version lll débordait de 236 pt.
- **2 protocoles expérimentaux** condensés (2DES+SLM à 750/820 nm mesurant τ_c 280→420 fs ; TR-SERS NPoM surveillant les modes 180/1145 cm⁻¹ et Φ_global = 0.971).
- **Methods (SERS scaling limits)** : phrase de renvoi vers tab:exp_benchmark pour situer EF=44 dans la plage expérimentale 10²–10³.
- **Limitations** : justification PQC vs BB84 importée de QST — « software-based post-quantum cryptography offers a lower-cost alternative, the physical BB84 protocol provides information-theoretic security immune to algorithmic cryptanalysis on resource-constrained embedded nodes (ARM Cortex-M4) ».
- **references.bib** : +2 entrées copiées depuis la bib QST (Brixner2005 Nature 434, 625 ; Baumberg2019 Nat. Mater. 18, 668) — DOI vérifiés côté QST, bibtex 0 warning.
- **Correction au passage** : « eight breakthroughs » (erreur du journal §12) → rétabli **« nine breakthroughs »** (9 sous-sections vérifiées dans le roadmap SI).

**Build : 0 erreur, 0 undefined, 0 overfull — main 35 pp (corps 6 956 mots < 7 000), SI 24 pp, cover 4 pp, bibtex 0 warning.**

---

## 14. Application log 2026-09-23 (cover AE benchmark + backport mutuel AE ↔ QST)

**Lot 1 — Cover letter AE (benchmark expérimental) :** bullet « Experimental testability » ajouté à la liste des contributions (tableau benchmark 6 lignes + 2 protocoles de validation : 2DES+SLM 750/820 nm, TR-SERS NPoM) — le relecteur AE dispose désormais d'une réponse explicite « comment falsifier/valider ? ». Cover recompilée : 0 erreur, 0 overfull, 4 pp.

**Lot 2 — Backport AE → QST (sens inverse), avec découverte pivot :** le main QST portait un **vintage de données obsolète sans facteur 2** (Table 2 : 0.097→0.183→…→0.160, narratif « local peak à 0.4 nm³ »), alors que (a) le HDF5 de production et la table comparative QST sont au vintage corrigé (0.0799 à 1.2 nm³) et (b) le journal d'audit QST §Table 2 tranche pour 0.0799 (−91.8 %). Le main QST se contredisait donc lui-même (L243 disait déjà 0.080). Normalisation complète :
- **Eq. (phi_ft)** du main QST : préfacteur 2 ajouté + « the prefactor 2 accounts for the two trapping sites » (aligné sur le code `orchestrator.py` L472 et l'Eq. SI).
- **Table 2** réalignée sur le dataset canonique 7 points AE (0.0505…0.0799, monotone) + ligne 1.4 nm³ ; colonne Φ_global recalculée = 0.971 partout (0.99×0.980+0.01×Φ_NPoM) — les « 97.1–97.2 % » issus du vintage deviennent « 97.1 % » invariant.
- **Narratif volume scan** (main + SI S-panels) : pic local 0.183/creux 0.146 supprimés → croissance monotone avec diminishing returns ; « four-order-of-magnitude » → « three-orders-of-magnitude » (33 à 1.6×10³, plage réelle).
- **SI** : paragraphe « Plasmonic suppression » 0.1599/83.7 % → 0.0799/91.8 % ; g₀ inchangé à 1.2 nm³ (109.5 cm⁻¹), 101.4 cm⁻¹ ajouté à 1.4 nm³ (déduit de g₀∝V^(−1/2)).
- **Corrections canoniques identiques à AE** : η_shield (1−η) avec résidu 15 % explicite (main L291 + Methods L440 + SI thermal) ; 15 % de gain (POC main + SI) ; 650 m³/yr redérivé du crédit 1300 L/m²/yr (main POC + QAOA + SI + cover) ; dual-OPEX conservé (usage QST légitime).
- **Table comparative QST** : mention « limiting case » (caption) + footnote n=2 retirée.

**Lot 3 — Restauration figures QST (package livré sans dossiers figures) :**
- Détail : `Figures` était un **symlink cassé** vers `figures/` inexistant ; reconstruit `figures/` + symlink.
- 4 figures main : Figure1/2/3 extraites du main QST original (HEAD git, pages 15–16, pdfimages + fusion smask/RGB) ; `Figure_Setup_Dispositif.png` copié depuis AE (même actif, même rendu).
- 5 figures SI : 2 copiées depuis AE (Compara 4Runs, NPoM ON vs OFF) ; `Figure_SI_Population_Dynamics_Local.png` extraite du SI original (sans annotations de vintage) ; **`Figure_SI_NPoM_VolumeScan_n20.png` régénérée** via `plot_volume_scan_light.py` **corrigé au passage** (il codait en dur le vintage 0.097→0.183→0.160 !) avec les données canoniques 7 points ; **`Figure_SI_Coupling_Regime_Diagram.png` régénérée** via nouveau script `plot_coupling_regime.py` (générateur d'origine disparu) — schéma de mécanisme, pas de chiffres de rendement vintage.
- Table S-FAO56 (SI) : 82.8 pt d'overfull (en-têtes longs) → en-têtes raccourcis + \small + tabcolsep 4pt.

**Lot 4 — Auto-correctifs AE découverts pendant le backport :**
- Main AE trace-conservation : « baseline NPoM-off run (n=100) » → **n=20** (la table comparative donne n_traj=20 pour NPoM-off ; la phrase de la légende limitait le n=100 à V=0.8).
- Main AE Limitations : « the probe experiences only 85 % of the ambient greenhouse temperature fluctuation » → **15 %** (même inversion η_shield que QST — restée invisible au lot §12 car la formulation différait de celle du SI).

**Build final :**
- **AE : main 35 pp, 0 erreur, 0 undefined, 0 overfull, bibtex 0 warning ; cover 4 pp, 0 erreur, 0 overfull.**
- **QST : main 20 pp, 0 erreur, 0 undefined, bibtex 0 warning, overfull ≤ 7 pt (4, cosmétiques) ; SI 30 pp (= original), 0 erreur, overfull résiduels cosmétiques (< 6 pt) ; cover 2 pp, 0 erreur, 0 overfull.**

**À vérifier par l'auteur :** les 2 figures régénérées (VolumeScan, CouplingRegime) et la figure de dynamique extraite du PDF (rendu) ; la valeur g₀=101.4 cm⁻¹ à 1.4 nm³ (déduite de g₀∝V^(−1/2), le run 1.4 n'étant pas dans le script d'origine 6 points).

---

## 15. Application log 2026-09-23 (cover 1 page + terminologie Elsevier)

**Terminologie :** « Supporting Information » (terme ACS/Nature) → **« Supplementary Material »** (terme Elsevier/AE) dans le SI (titre + paragraphe d'accompagnement) et la cover. Vérifié sur le Guide for Authors AE (ScienceDirect, archivé) : la checklist de soumission liste « *Supplemental files (where applicable)* » — le matériel supplémentaire est bien accepté, la dénomination seule était non conforme. Le main ne contenait aucune occurrence (0).

**Cover letter AE : 4 pp → 1 page.** Réécriture condensée structurée sur les **5 questions imposées par le Guide for Authors** (nouveauté / lectorat / importance / vérification native speaker / disponibilité comme relecteur) : paragraphe « Significance », 4 bullets « Key advances » (dont benchmark expérimental + protocoles), « Why Applied Energy? », paragraphe fusionné « Novelty, compliance, and declarations », reviewers suggérés en une ligne (avec domaines), enclos sur une ligne (Manuscript, Supplementary Material, Highlights, Graphical Abstract). Réductions : 12→10 pt, marges 2.5→2 cm, `enumitem` nosep, suppression des enclos de figures individuelles et des redondances (79–84 % conservé). Gates : **0 erreur, 0 overfull, 1 page.**

---

## 16. Correction majeure 2026-09-23 (facteur 2 INVALIDÉ par les données brutes HPC) — supersède §12/§13/§14 sur ce point

**Contexte.** Vérification « ±0.0005 contre les sorties brutes » (restée à charge de l'auteur au §12) exécutée sur le HPC (`nanaengo@100.73.21.40:~/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2`) : 8 HDF5 + CSV de scans.

**Preuve (reproduction exacte des deux ères par la ligne `rc_yield` du code).** Avec γ_RC = 0.15 /ps et dt = 0.2 fs :
- Runs **juin** : `rc_yield = γ·Σtrapped_pop·dt` **sans facteur 2** → 0.0768 (Jun24), 0.0803 (Jun26/295K), 0.168473 (77K) — tous reproduits à 1e-4, = valeurs publiées.
- Runs **juillet** (scan_A*) : code modifié entre-temps avec `2.0*gamma_rc` → 0.1220/0.1463/0.1522 stockés, = **2×** les valeurs de table (÷2 → 0.0610/0.0731/0.1522÷2… retombent sur la courbe canonique 0.0605/0.0727/0.0761).
- `baseline_N20.h5` stocke 2.0056 (>1, non physique) : tournée avec le code bogué de l'ère juillet. Le 0.9800 publié = `phi_ft_passive` (constant du code), pas le `rc_yield` cru.
- HDF5 local `data/converged/production_dynamics.h5` (0.0803) : ère juin, reproduit exactement par le code corrigé.

**Verdict.** La définition canonique — celle de TOUTES les tables publiées — est **Φ_FT = Γ_RC ∫(P₃+P₄)dt sans préfacteur**. Le « facteur 2 » introduit dans le code entre juin et juillet est un bug de double comptage (la baseline >1 en est la signature). Les équations « corrigées » avec préfacteur 2 aux §12–14 étaient fondées sur le code bogué : **inversées**.

**Corrections appliquées :**
- Main AE + main QST : Eq. (3)/Phi_FT — préfacteur 2 retiré + phrase « prefactor 2 » supprimée.
- SI AE + SI QST : Eq. (SI_phi_ft) `2Γ` → `Γ` + note « two trapping sites » réécrite (les deux sites sont sommés dans l'intégrande).
- Code : `src/orchestrator.py` L177/L472 `2.0*gamma_rc` → `gamma_rc` + commentaire §6c corrigé ; `src/digital_twin.py` L109 idem. Syntaxe vérifiée.
- Aucune table ni chiffre publié n'est affecté : ils correspondent tous déjà à la définition sans facteur 2 (canon inchangé).

**Statut des items §12/§13/§14 (« préfacteur 2 ajouté ») : supersédés par le présent §16.**

**Suite §16 — outillage aligné sur le canon (2026-09-23) :**
- `../Submission_Package_QST_Manuscript/verify_acceptance.py` : rendu portable (chemins relatifs au script au lieu de `/home/taamangtchu/...` codés en dur) + **5 nouveaux contrôles de canon** : Eq. Φ_FT sans préfacteur 2 dans le main et le SI, zéro résidu « factor of 2 »/« 2Γ_RC », valeur canonique 0.0799 présente (main + SI), zéro vintage obsolète (0.1599/83.7 %/0.183). **22/22 checks PASS.**
- `README_AppliedEnergy.md` : réécrit (état 2026-09-23 : manuscrit audité, SI retitré « Supplementary Material », cover 1 page) + bloc « Numerical canon » (définition sans facteur 2, 0.0799, 15 %, 650 m³, avertissement HDF5 scan_A* ×2).
- `Submission_Package_QST_Manuscript/README.md` : créé (absent) — contenu, restauration des figures, historique de réconciliation, même bloc « Numerical canon », invocation de `verify_acceptance.py`.
- README racine : 0 mention de rendement — non concerné.
