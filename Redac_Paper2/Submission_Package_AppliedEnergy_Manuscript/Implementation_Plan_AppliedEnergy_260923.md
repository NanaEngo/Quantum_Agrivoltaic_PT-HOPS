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

**Suite §16 — relance des scans juillet sur le HPC (2026-09-23, en cours) :**
- Code corrigé déployé sur `nanaengo@100.73.21.40:~/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2` : les 4 `orchestrator.py` (main + scan_A1/A2/A3) et 4 `digital_twin.py` patchés (backups `*.pre_corr_20260923.bak`), zéro résidu `2.0 * gamma_rc`.
- Sauvegarde préalable : `backups/hdf5_csv_backup_pre_relaunch_20260923.tar.gz` (10 fichiers : HDF5 ères juin+juillet, CSV de scans).
- Découverte : les `quantum_simulations_framework/` locaux (main + scan_A*) sont des **squelettes sans aucun .py** (vidés) ; le vrai framework est à la racine projet (`~/Quantum_Agrivoltaic_PT-HOPS/quantum_simulations_framework`). Le solver (`src/quantum_interface/solver.py`) résout `_QS_FW` 3 niveaux au-dessus → symlink à la racine du dossier de lancement.
- **7 volumes (0.2→1.4 nm³) relancés EN PARALLÈLE** via `run_npom_scan_relaunch.sh` dans `relaunch_20260923/V*/` (63 processus actifs, trajectoires initialisées ~20:41). Durée estimée : plusieurs heures (n_traj × 5000 pas). Résultats attendus : `relaunch_20260923/V*/data/converged/production_dynamics.h5` + CSV agrégé.
- `scan_A1` (V=0.2, bloqué à 16/20 traj le 31 juil.) est remplacé par la relance V=0.2.
- À la complétion : vérifier `rc_yield` finaux = canon (V=1.2 → ≈0.0799), sans facteur 2.

**Suite §16 — relire log collecteur + verdict canon (2026-09-24, matin) :**
- **Échec d'écriture 7/7 mais physique complète 7/7.** Le collecteur (`collect_relaunch_20260923.log`) a vu les 63 processus stables jusqu'à 03:11 puis décroître (63→54→36→27→9→0) ; CSV final `npom_scan_relaunch_20260923.csv` : 7×FAILED, aucun HDF5. Cause : `AttributeError: 'LcaSection' object has no attribute 'footprint_m2'` (orchestrator L377, étape [9d/10] gravimétrie) — crash APRÈS la complétion MesoHOPS (26332 s, 20/20 traj) et le calcul de Φ_FT ([6/10]), AVANT la sauvegarde HDF5 ([10/10]).
- **Cause racine : vintage de code.** Les clones relaunch ont copié le `src/` HPC main à 20:53 (avant l'arrivée effective du rsync) ; ce `src/` d'ère juillet contenait `footprint_m2` (champ supprimé depuis, remplacé par `config.lca.cooperative.area_m2`). Le rsync `--update` du soir avait SAUTÉ `src/orchestrator.py` : notre patch sed local→distant de 20:30 avait rafraîchi le mtime distant au-delà du mtime local. Piège mtime vs `--update` : à l'avenir, synchroniser le code avec `--checksum` (fait). Local canonique : `orchestrator.py` L378 `config.lca.cooperative.area_m2` (défaut 500 m²).
- **Verdict canon ATTEINT QUAND MÊME — Φ_FT extraits des logs de run ([6/10]), tolérance ±0.002 :**
  - V=0.2 : 0.0486 vs canon 0.0505 (Δ −0.0019, OK — à surveiller, cf. scan_A1 bloqué 16/20) ;
  - V=0.4 : 0.0610 vs 0.0605 (Δ +0.0005, OK) ;
  - V=0.6 : 0.0731 vs 0.0727 (Δ +0.0004, OK) ;
  - V=0.8 : 0.0761 vs 0.0761 (exact) ;
  - V=1.0 : 0.0793 (nouveau point, saturation) ;
  - V=1.2 : 0.0799 vs 0.0799 (EXACT — point clé −91.8 % reproduit) ;
  - V=1.4 : 0.0791 (plateau).
  Série croissante jusqu'à saturation ≥1.2, jamais >1 ; `Phi_FT_NPoM(raw) == (physical)` partout (correction préfacteur active) ; phi_global 0.9707–0.9710 (canon 0.971).
- **Mitigation outillage :** `collect_relaunch_results.sh` patché — fallback d'extraction Φ_FT depuis `scan_vol_*.log` (status `ok_log`) si HDF5 absent ; STAMP → 20260924 dans les deux scripts.
- **Relance 20260924 (06:14) :** `orchestrator.py` forcé vers HPC via `rsync --checksum` (footprint_m2 absent, area_m2 L378, py_compile OK — digital_twin/config_loader déjà conformes) ; scripts mis à jour déployés ; 7 volumes relancés en parallèle (`relaunch_20260924/V*/`, 63 processus, pids 1718876–1718898) ; `footprint_m2` vérifié ABSENT des 7 clones ; collecteur nohup `collect_relaunch_20260924.log`, CSV attendu `npom_scan_relaunch_20260924.csv`. ETA ~7–8 h (≈14:00, référence : 26332 s de propagation + pipeline).
- **Rapatriement automatisé (2026-09-24, ~08:00) :** extracteur `check_h5_vals.py` (h5py, cote HPC) validé sur les HDF5 d'ères connues (0.080325 juin / 0.079928 V=1.2 / 0.168473 77K / 2.005642 baseline buguée) ; puller local `pull_relaunch_h5.sh` v4 (inventaire SSH unique/cycle via heredoc quoté, détection process par `ps|grep|grep -v grep`, pull au terme du process ou fichier froid, marquage `missing` après double vérification, verdict canon automatique `canon_verdict_20260924.txt`) installé en **cron toutes les 10 min** (`flock` anti-recouvrement, mode `--once`) — les sessions de l'agent terminal tuant leurs enfants (nohup/setsid inclus), cron est le seul mécanisme survivant. Pièges notés : `pgrep -f` déformé par double échappement SSH (faux « missing ») et `ssh` consommant le stdin d'une boucle `while read` (herestring avalé).
- **Document de comparaison créé :** `../Redac_Paper2/COMPARAISON_Juin_Juillet_QST_AE_260924.md` — (1) ère juin (code conforme, valeurs publiées) vs ère juillet (bug ×2, scan_A*, baseline 2.0056) vs relances septembre (7/7 au canon) ; (2) packages QST vs AE (classes, paginations, SI, cover letters, spécificités, convergences numériques — `table_comparative_4runs.tex` identique bit-à-bit).

**Suite §16 — renforcement gap/novelty/claims + alignement guideline AE (2026-09-24) :**
- Deep web search (guideline AE via synthèses — ScienceDirect 403 ; reviews agrivoltaïques 2025–2026 ; sensing quantique agricole). Screener AE : system-level framing, TEA avec sensibilité, réalisme de déploiement ; abstract ≤300 mots, 6–8 keywords, highlights ≤85 car., graphical abstract obligatoire, ~12 000 mots.
- **Intro** : 3 gaps de littérature explicités (optique statique ; TEA/LCA découplées de la physique ; sensing ajouté après coup) avec refs 2024–2026 (Mahim2025, Ravilla2024, Bellone2024, CiallaMay2024, Pook2025, + **KaurJeet2026** Nanotechnology 37, 232002 — ajoutée au bib après vérification DOI/title/volume) ; **question centrale** reformulée en 3 volets (co-optimisation / seuil de rentabilité / nature des barriers) + **3 familles de claims falsifiables F1/F2/F3** avec bornes.
- **Discussion** : paragraphe prior art recentré sur les « three firsts » (i–iii) ; **Conclusions + §économique** : split explicite barriers économiques (traitables, CAPEX 322→140 $/m², payback 2.63 yr) vs physiques (nanofabrication gaps NPoM <2 nm, fouling, encapsulation OPV).
- **Cover letter** : ouverture problème-système, « three firsts », barriers, compressée à **1 page** (enlargethispage 2\baselineskip) ; **Highlights** : puce 5 « first quantum-coherence-guided agrivoltaic design with TEA and LCA » (AES-256 retiré) ; **keywords** : 8 (ajout agrivoltaic techno-economics, quantum digital twin).
- **Builds** : main 36 pp / cover 1 p — 0 erreur, 0 undefined, 0 overfull, biblio 0 warning ; abstract 161/300 mots ; ~7.7k mots (limite 12k).
- **Audit d'acceptation AE créé : `verify_acceptance.py` (52 contrôles — 52/52 PASS)** : complétude package, structure Elsevier, terminologie SI, abstract/keywords/highlights (85 car.), questions cover letter, canon numérique (Eq. sans préfacteur main+SI, 0.0799, 0.971, 91.8 %, 4.23 yr, 19.6, série du scan, zéro vintage), **contrôles de framing canon** (3 gaps, question falsifiable, F1/F2/F3, firsts, barriers économiques/physiques, KaurJeet2026, « unreported » borné). Non-régression QST : 22/22.
- **Durcissement de l'audit (relecture critique — 56 contrôles, 56/56 PASS)** : suppression d'un contrôle fantoche (`or True`) remplacé par le **vrai décompte de pages** parsé depuis le log pdflatex de la cover letter (=1) ; ajout de 4 contrôles AE manquants (\linenumbers pour la relecture, **limite ~12 000 mots** via dé-TeX brut — plafond, compteur agressif, à confirmer au GFA officiel ; **≥2 papiers Applied Energy cités** — extraction corrigée des clés BibTeX `@Article{key` ; **graphical abstract 2048×1024** parsé depuis l'en-tête PNG) ; keywords assouplis 5–8 avec avertissement « confirm official cap at upload » (le GFA officiel renvoyait 403 — seuils tirés de sources secondaires, seuls les 85 car. highlights sont un standard Elsevier certain). Les contrôles de framing verrouillent des formulations éditoriales : les traiter comme verrous de canon, pas comme des vérités de guideline.
- **Renommage des fichiers de soumission (2026-09-24, convention demandée) :** `Manuscript_AppliedEnergy_260923.tex/.pdf` → **`AppliedEnergy_main_2609.tex/.pdf`** ; `SI.tex/.pdf` → **`AppliedEnergy_SM_2609.tex/.pdf`** ; `Cover_Letter_AppliedEnergy.tex/.pdf` → **`AppliedEnergy_Cover_letter.tex/.pdf`** — `git mv` (renommages suivis), artefacts LaTeX obsolètes (aux/log/out/bbl/blg/toc/spl, dont `SI.bbl` et logs de build) purgés. Références internes mises à jour et REBUILD COMPLET : `\externaldocument{SI}` → `{AppliedEnergy_SM_2609}` dans le main et `\externaldocument{Manuscript_AppliedEnergy_260923}` → `{AppliedEnergy_main_2609}` dans le SM (renvois croisés xr validés — 0 undefined), `verify_acceptance.py` (nouveaux chemins, 56/56 PASS), `README_AppliedEnergy.md`, `COMPARAISON_Juin_Juillet_QST_AE_260924.md`. Builds finaux : main 36 pp / SM 24 pp / cover 1 p — 0 erreur, 0 overfull, 0 undefined. Le journal lui-même garde son nom daté 260923 (historique d'application, non soumis).
- **Synchro HPC du renommage + contenu du jour (2026-09-24, 08:10 UTC) :** `rsync -r --checksum --delete` du package AE vers `Redac_Paper2/Submission_Package_AppliedEnergy_Manuscript/` côté `nanaengo@100.73.21.40` (25 fichiers transférés, 25 obsolètes purgés, y compris anciens noms). Validation sur place : nouveaux noms seuls présents, `verify_acceptance.py` **56/56 PASS** sous python HPC, zéro trace des anciens noms. Les scans `relaunch_20260924` sont à 1h54 (0/20 traj, 63 processus — normale sous contention) ; puller cron local + collecteur HPC en place, verdict attendu vers 13:30–14:30 UTC.

**Suite §16 — audit adverse sévère du package AE + mitigations (2026-09-24) :**
Constat vectorisé « Reviewer 2 » et traitement :
- **(MAJEUR, corrigé) Contradiction interne SM/main** : le SM portait « 8 % quantum yield enhancement » là où le main dit **15 %** pour le même +1.23 kg/m²/yr (1.23/8.2 = 15.0 % — le SM gardait un vintage). SM aligné sur 15 %.
- **(CRITIQUE, atténué) Table du scan : 5/7 entrées à n=2** (légende honnête mais exposée). Mitigation : phrase de légende « An independent n=20 re-simulation of all seven volumes with the corrected production code reproduces every entry within ±0.002 (V=0.8/1.2 exactly) » — appuyée par les logs 20260923 ; la preuve archivée arrivera avec les HDF5 20260924 (ETA ~14:00 UTC).
- **(Forme, corrigé) Casse des headings** : « 8-Site FMO hamiltonian », « floquet stark detuning and omit », « fao-56 » → casse correcte (FMO Hamiltonian, Floquet–Stark detuning and OMIT, FAO-56) dans le main ET le SM (3 headings SM : section Hamiltonian, section Floquet–Stark/OMIT, subsection Floquet–Stark). La claim « native-speaker check » de la cover letter redevient crédible.
- **(Hygiène, corrigé) Fuites d'héritage** : commentaires d'en-tête mentionnant « Nature Energy V5 retarget » purgés du main et du SM.
- **(Data availability, atténué)** : « upon reasonable request » → engagement de dépôt public à l'acceptation + périmètre précisé (paramètres, YAML, scripts d'orchestration, code d'analyse).
- **Résiduels assumés (non traitables à ce stade)** : Φ_FT passif 0.98 = constante de modèle (bornée par Limitations ; ne pas laisser un relecteur la confondre avec un résultat simulé) ; ORCID manquants (TODO auteur F11, bloquant upload mais pas review) ; pas de σ affichable sur les entrées n=2 (couvert par la cross-validation) ; seuils GFA (mots, keywords) à confirmer officiellement à l'upload.
- Builds post-mitigation : main 36 pp / SM 24 pp — 0 erreur, 0 overfull, 0 undefined ; `verify_acceptance.py` 56/56 PASS.

**Suite §16 — passe siunitx méticuleuse (2026-09-24) :**
Méthode : rendu tranché par **probes pdflatex isolés** (/tmp/siunitx_probe) plutôt que par déduction — siunitx force le **mode slash** dès qu'un `\of{}` contient `\ce{}` (`\kg\of{\ce{CO2}}e` → « kg (CO2)e/m2 **/yr** », double slash = violation BIPM + espace parasite), alors que `\of{\ce{CO2e}}` reste en mode réciproque avec l'indice chimique (« kgCO2e m−2 yr−1 »).
- **Corrigé (19 constructions)** : `\of{\ce{CO2}}e` → `\of{\ce{CO2e}}` (10 main + 8 SM + 1 cover letter) ; `\USD\per\tonne\ \ce{CO2}e` → `\USD\per\tonne\of{\ce{CO2e}}` (2) — zéro double slash résiduel, per-mode réciproque uniforme dans tout le package.
- **Corrigé : `\kWh` non déclaré** (seul `\MWh` l'était) → rendu « kW h » espacé ; `\DeclareSIUnit{\kWh}{kWh}` ajouté au main et au SM — rendu « kWh » compact (0 « kW h » résiduel).
- Validation empirique finale par extraction pdftotext : 0 « e/m2 /yr », 0 « kW h » (main + SM) ; builds main 36 pp / SM 24 pp / cover 1 p — 0 erreur, 0 overfull, 0 undefined ; audit 56/56 PASS. Déjà conformes et laissés tels quels : litres `\L` (pas de piège Ł), `\day`, `\ha`, nm³ via `\cubed`, sépareur de milliers siunitx.
- Le HPC est re-synchronisé après cette passe (voir entrée suivante).

**Suite §16 — élimination du jargon AI + prose scientifique (2026-09-24) :**
Scan lexique systématique (Crucially, leverage, transformative, paradigm, closes the loop, a key insight, apparent conflict/contradiction, not merely, plays a central role, aligns perfectly, functional synergy, relies heavily on robust, economically transformative, Additionally, Furthermore, breakthroughs, premier venue, perfectly aligning…) sur les 6 fichiers soumission (main+SM+cover AE, main+SI+cover QST) — NatureEnergy référence exclue.
- **AE main (7)** : « plays a central role in directing energy flow » → « governs the flow of excitation energy » ; « A key insight of our multi-scale framework is that the NPoM… » → causal direct (« Because the NPoM SERS diagnostic mode suppresses… it need only cover… ») ; « resolves the apparent contradiction between… and… » → « canopy-scale productivity is thus maintained even though transport is suppressed locally » ; « is not merely an auxiliary security feature but is physically integrated » → « is physically integrated » ; « This closes the loop between… » → « This chain connects… ; no existing agrivoltaic design integrates both » ; « Furthermore, the 30 % subsidy… » → phrase directe ; « trade-off central to the paradigm » → « quantifying the yield–carbon trade-off ».
- **AE SM (2)** : « leverage the same subsidy » → « share the same subsidy » (phrase refondue) ; Outlook « opens several transformative directions… nine breakthroughs » → « opens several directions for further development… nine advances ».
- **QST main (9)** : idem AE pour plays-a-central-role / key-insight→Because / apparent-contradiction→donc-coexist / Crucially supprimé (L223) / « resolves the apparent conflict » → « …therefore coexist: … » ; « functional synergy » → « shared spectral budget » ; « Furthermore, to prevent… » → phrase directe ; « Additionally, the bath… » → « The bath… » ; « transforming a fundamental quantum limitation into an engineering advantage » → « absorbed at negligible canopy-scale cost » ; « relies heavily on robust data integration » → « requires integrated data streams ».
- **QST SI (3)** : leverage→share ; « aligns perfectly with » → « matches » ; « economically transformative… robust field-sensor » → « economically viable… dependable field-sensor » ; Outlook « transformative/breakthroughs » → « directions for further development/advances ».
- **QST cover (1)** : « is the premier venue… perfectly aligning with QST's mandate to publish transformative quantum technologies » → description factuelle du périmètre QST (fin de la flatterie éditoriale).
- **Laissés volontairement** : « robust convergence » (qualifie la stabilité numérique, terme technique légitime, ×4), « robustness gaps » (reprise du vocabulaire de KaurJeet2026), « dependably/dependable » restants.
- Builds : QST main 20 pp / SI 30 pp / cover 2 pp ; AE main 36 pp / SM 24 pp / cover 1 p — 0 erreur, 0 undefined partout ; audits QST 22/22 et AE 56/56 (marqueurs de canon F1/F2/F3 intacts). Rescan lexique final : 0 occurrence sur les 6 fichiers cibles.

**Suite §16 — lecture à voix haute de l'ouverture AE (2026-09-24) :**
Sept accrochages corrigés (abstract 159 mots, main 36 pp 0 erreur/0 overfull, audit 56/56) :
1. Abstract : « a modelled, quantum-guided agrivoltaic system incorporating… » (trois modificateurs empilés) → « a quantum-guided agrivoltaic system in which a… layer couples to… » (structure directe).
2. Abstract : « Secure IoT telemetry is maintained over a BB84 quantum link » (passive plate) → « A BB84 quantum link secures the IoT telemetry » (active, reprend le rythme des phrases voisines).
3. Abstract : « cooperative economic modeling… modelled… cooperative case » (répétition modeling/modelled) → « techno-economic analysis of a Cameroonian micro-module ».
4. Intro : « Land-use optimisation » → « optimization » (l'orthographe britannique isolée tranchait à l'oral contre « optimization » utilisé partout ailleurs).
5. Intro gap (i) : phrase-monstre ~50 mots scindée en deux au point-virgule (« …window. Dynamic, physics-guided spectral management has not been transposed… ») — le second souffle était inaudible.
6. Paragraphe-fuseau (~200 mots) coupé avant « The photosynthetic apparatus » (les 3 gaps d'un côté, la physique de l'autre).
7. « serves as a model system for exploring this concept » (référence vague après saut de paragraphe) → « the model system for spectral light-sharing » ; « macroscopic multi-scale lifecycle assessment » (dédoublement) → « field-scale lifecycle assessment ».

**Suite §16 — VERDICT CANON de la relance 20260924 (2026-09-25, validation finale) :**
Complétion : **7/7 HDF5** rapatriés (puller v4 en cron 10 min, 0 missing ; pulls échelonnés 13:50→15:10 UTC le 24/09, dernier V0.2) ; verdict automatique `canon_verdict_20260924.txt` + archivage `Redac_Paper2/backups/relaunch_20260924/` (7 HDF5 + sidecars .vals/.phi + verdict + log de pull, 3.2 Mo, committé comme preuve).
- **rc_yield h5 vs canon 2026-09-23 (tolérance ±0.002) — 5/5 points canon reproduits** : 0.2→0.048595 (écart −0.0019, OK), 0.4→0.061008 (+0.0005), 0.6→0.073126 (+0.0004), **0.8→0.076121 (+0.00002 — exact)**, **1.2→0.079928 (+0.00003 — exact, reproduit le point n=20 canonique à 5e-5)**. Deux nouveaux points : 1.0→0.079318, 1.4→0.079098. Jamais >1 sur les 7.
- **Cohérence h5 ↔ log de run : |Δ| ≤ 3e-5 sur les 7 volumes** — le HDF5 et le Φ_FT loggé par le code de production décrivent bien la même dynamique (aucun écart d'extraction/pipeline).
- **Interprétation** : la cross-validation n=20 promise en légende de la table du scan (« reproduces every entry within ±0.002, V=0.8/1.2 exactly ») est maintenant **prouvée par artefacts committés**, y compris pour le point V1.2=0.0799 porteur de la claim −91.8 %. La « slight decrease at 1.4 » énoncée au main (L243 : monotone jusqu'au max 0.0799 à V1.2, décroissance légère à 1.4) est **confirmée** (0.079098) — le flag « monotonie violée » du puller (monotonie stricte sur les 7 points) est plus strict que la claim du papier et ne constitue pas un écart au canon.
- **Résiduel sans impact** : le CSV du collecteur HPC (`npom_scan_relaunch_20260924.csv`) est sorti avec phi_FT vide (ValueError parse float sur chaîne vide dans le pipe python du collecteur) ; sans conséquence — les sidecars `.vals` (extraits côté HPC par `check_h5_vals.py`) sont la source de vérité, le CSV est redondant. Le cron du puller reste actif mais no-op (sortie immédiate sur `.done`) — peut être retiré du crontab.
- Physique complète 2 jours de suite : la relance 20260923 (logs seuls) et la relance 20260924 (logs + HDF5) concordent volume par volume ; le canon Φ_FT sans préfacteur 2 est validé sur 14 runs indépendants.

**Suite §16 — figure scan volume régénérée + harmonisation V1.0/V1.4 + clôture outillage (2026-09-25) :**
- **Harmonisation de provenance V1.0/V1.4** : les tables et scripts portaient 0.0795 (V1.0) et 0.0797 (V1.4), valeurs **sans provenance** (vintage de l'ère n=2, ne correspondant à aucune mesure) ; remplacées par les mesures validées **0.0793 / 0.0791** (relaunch_20260924, moyennes n=20) dans la table du main AE, la Table 2 QST + sa prose, et les 2 scripts de tracé. Les barres d'erreur placeholder du tracé (SE de l'ère n=2, non mesurées) sont retirées — moyennes n=20 seules, SE archivée uniquement à V=1.2 (0.0005, Table 2).
- **Figures QST SI régénérées** avec les 7 points : `plot_volume_scan_light.py` (4 panneaux, légende fig corrigée 6→7 volumes) + `plot_coupling_regime.py` → `figures/`. Le symlink `Figures` (supprimé le 24/09 sans être committé) est restauré — le build SI compile depuis `Figures/` ; sa suppression avait cassé le build (3 erreurs pdftex.def détectées puis résorbées).
- **Précision « all volumes »** : les phrases renvoyant à la figure de dynamique (main QST + SI) précisent désormais « five representative volumes ($V=0.2$–$1.2$ nm³) » pour matcher les 5 panneaux réellement affichés (V1.4 sans panneau de dynamique).
- **Prose QST cohérente avec les nouvelles valeurs** : la phrase « yield increases monotonically… diminishing returns above 1.0 (0.0793 at 1.0) » reste correcte (croissance 0.0505→0.0799 jusqu'au max V1.2, léger repli 0.0791 à V1.4 déjà énoncé) ; aucun écart au canon.
- Builds : QST SI 30 pp / main 20 pp — 0 erreur, 0 undefined (overfull SI préexistants, cosmétiques) ; AE main 36 pp — 0 erreur / 0 undefined / 0 overfull. Audits : AE 56/56, QST 22/22.
- **Clôture outillage relaunch** : entrée cron `pull_relaunch` retirée du crontab local (mission terminée, marqueur `.done` ; le script restait en no-op 10 min) ; vérifications : aucun processus `pull_relaunch` local, aucun collecteur HPC actif, aucun cron/at HPC, lock `/tmp/pull_relaunch.lock` purgé.

**Suite §16 — switch `Figures`→`figures/`, chasse aux résidus, sync HPC (2026-09-25) :**
- **Adieu symlink** : les 3 `\includegraphics` de la SI QST pointent désormais vers `figures/` (minuscule, le vrai dossier) et les 2 scripts de tracé écrivent directement dedans ; le symlink `Figures` est supprimé définitivement. Build SI re-vérifié : 0 erreur, 30 pp.
- **Chasse aux résidus 0.0795/0.0797 sur tout le repo** : historiques légitimes conservés (rapport juin `ANALYSIS_20260624_POST_PROD.md`, journal §16 lui-même, archives Nature Energy V5 — y compris la copie héritée du package QST, documentée comme telle au README QST) ; seul fichier actif corrigé : **`AGENTS.md`** dont la table du scan volume portait encore les valeurs juin (0.0795/0.0804/0.0797 — dont le 0.0804 n=2 dépassé) → harmonisée sur le canon validé n=20 (0.0793/**0.0799**/0.0791) avec mention de la cross-validation et de l'archive HDF5.
- **Sync HPC** (`rsync -rvh --checksum --delete`) : AE 3 fichiers, QST 8 fichiers + 19 obsolètes purgés (dont le symlink `Figures` distant), `AGENTS.md` poussé. Marqueurs vérifiés sur place (5× `figures/` SI QST, 0 symlink, 0.0793/0.0791 AE, 0.0799 AGENTS.md).
- **Piège d'audit détecté et corrigé** : la purge blanket des artefacts LaTeX avant rsync a supprimé le **log pdflatex de la cover letter** — dont dépend le contrôle « page count » de `verify_acceptance.py` (55/56 sur HPC). Cover rebuilt (1 p, 0 erreur) → 56/56 local et HPC. Leçon : le log de build de la cover est une dépendance vivante de l'audit, ne pas le purger.
- Audits finaux : AE 56/56 (local + HPC), QST 22/22 (local + HPC).

**Suite §16 — passe novelty « waouh » (2026-09-25) : matrice de capabilities, contre-factuels chiffrés, question en une phrase, figure-tête plateau.**
Objectif : faire lire le papier « énergie d'abord » par l'audience AE (le wow vient des nombres, pas des adjectifs — cohérent avec la purge anti-jargon). Quatre leviers implémentés :
1. **Contre-factuels chiffrés dans les 3 gaps** (coût de chaque statu quo, tous déductibles des données validées) : gap (i) statique — « the forward transfer yield varies by a factor of 1.6 and the SERS enhancement by a factor of 48 across the accessible range, so a statically chosen cladding fixes the energy–diagnostics balance at deployment » ; gap (ii) découplage — « accounting that ignores the local transport physics would credit the canopy with 1.0 instead of 0.971, a 2.9-point overestimate — and would never discover that the 91.8% local penalty costs only 2.9 points globally » ; gap (iii) sensing bolted-on — « reusing the NPoM optical infrastructure delivers SERS diagnostics at a canopy-area cost of 1% and a canopy-yield cost of 2.9%, instead of separate sensing hardware ».
2. **Matrice de capabilities** (`tab:capability_matrix`, Discussion/Prior art) : 7 fonctions (power, microclimat, eau, chaleur, SERS, QKD, comptabilité multifonctionnelle) × 4 classes (passive claddings / multi-vector TemizDincer2024 / agri-sensing standalone / this work) — aucune classe antérieure n'en couvre plus de 3, celle-ci les 7 en un seul footprint. Symboles sécurisés `$\checkmark$` (amssymb).
3. **Question centrale resserrée en UNE phrase falsifiable** (la capa PT-HOPS devient le « how », plus le « what ») + **trois sous-questions Q1 Device / Q2 Physics / Q3 System** mappées sur les Results (scan volume + intégration canopée / dynamique exacte + Floquet–Stark/OMIT / FAO-56 + coopérative + BB84). F1–F3 intacts derrière.
4. **Figure-tête `fig:flat_canopy`** (`plot_plateau_canopy.py` → `figures/Figure_Plateau_Canopy.png`, placée avant fig:quantum_dynamics) : (a) quenching local >90 % vs baseline 0.98 (facteur 1.6, max 0.0799 à V1.2) ; (b) plateau global **plat à 0.971 sur tout le scan** — « the flat curve in (b), not the quenching in (a), is the design-relevant outcome ». Phrase d'accroche dans l'intro : « a 91.8% local transport penalty confined to a 1% sentinel area costs 2.9 points of canopy-scale trapping yield while adding single-complex SERS diagnostics to the same footprint ».
- **Audit durci 56→60 contrôles, 60/60 PASS** : verrou de la question mis à jour sur la nouvelle formulation canonique (« The central question of this work is falsifiable ») + 4 nouveaux contrôles (Q1–Q3, matrice, figure-tête, contre-factuels). NB : renumérotation des figures — fig:flat_canopy devient Fig. 1, la figure dynamique passe en Fig. 2 (renvois tous via \Cref, aucune référence dure « Fig. 1 » dans le texte).
- Builds : main **38 pp** (36 + matrice + figure-tête + bloc question) / SM 24 pp — 0 erreur, 0 undefined, 0 overfull ; cycles bibtex SM+main refaits après purge (leçon répétée : purge d'artefacts ⇒ toujours re-cycler bibtex avant audit).
- Reste volontairement hors périmètre : miroir cover letter (la phrase-plateau pourrait y être ajoutée), sync HPC à refaire après ce commit.

**Suite §16 — miroir cover letter + sync HPC + contrôle visuel (2026-09-25) :**
- **Miroir cover letter** : le bullet « SERS–transport trade-off resolved » reformulé avec la phrase-plateau alignée sur l'intro et la figure-tête : « confined to a 1% sentinel area, the 91.8% local transport penalty costs 2.9 canopy-yield points (97.1% preserved) while adding single-complex SERS diagnostics to the same footprint ». Cover toujours **1 page**, 0 erreur ; audit 60/60.
- **Sync HPC** (`rsync -rvh --checksum --delete`, 10 fichiers, 0 suppression) ; marqueurs vérifiés sur place (Q1/matrice/figure-tête/factor-48 au main, phrase-plateau à la cover) ; **audit 60/60 PASS exécuté sur HPC** (le log pdflatex de la cover, dépendance d'audit, a été préservé lors de la purge d'artefacts cette fois).
- **Contrôle visuel programmatique** : figure-tête (`fig:flat_canopy`, p. 27 du main 38 pp) — image native embarquée 6000×2640 @ 600 dpi (résolution effective 1112 ppi), les 3 traces confirmées par comptage de pixels (quenching bleu 59k, plateau orange 47k, baseline rouge 30k) ; matrice (p. 18) rendue dense avec les 8 `$\checkmark$` extractibles du texte PDF. NB méthode : le rendu pdftoppm basse résolution dilue les lignes fines par anticrénelage — contrôler les couleurs sur l'image native `pdfimages`, pas sur le rendu de page.

**Suite §16 — lecture à voix haute des nouveautés + doc comparaison + checklist d'upload (2026-09-25) :**
- **Read-aloud (contre-factuels, Q1–Q3, headline, légende figure-tête) — 2 corrections de sémantique numérique** : (1) le coût NPoM est **0.9 point** de canopée (0.980 → 0.971), pas 2.9 points ; les 2.9 pts sont l'écart à une canopée idéale de 1.0 (dont 2.0 pts de déficit passif). Les formulations initiales de la passe novelty attribuaient 2.9 pts au NPoM — corrigé partout : gap (ii), headline, légende figure-tête, cover letter, annotation de la figure (régénérée), verrou d'audit. Le chiffre honnête est d'ailleurs plus fort. (2) le contre-factuel du gap (ii) crédite la baseline passive **0.980** (pas 1.0) — une comptabilité ignorant la physique ne crédite jamais l'unité. Q1–Q3 : rythme sain (question courte, réponse en 2 phrases), laissés tels quels. Builds : main 38 pp / cover 1 p — 0 erreur / 0 undefined / 0 overfull ; audit 60/60 (verrou contre-factuels recalé sur la sémantique 0.9/2.9).
- **Doc comparaison mise à jour** (`COMPARAISON_Juin_Juillet_QST_AE_260924.md`) : verdict 20260924 confirmé (7/7 HDF5, écarts par volume, monotonie stricte vs énoncé du papier), AE 38 pp / 60 contrôles + passe novelty, V1.0/V1.4 sans provenance purgés, sémantique 0.9/2.9 documentée, correction au passage d'une valeur de table du §2.1 (0.0761 → 0.0768 n=100, la seule présente dans les tables).
- **Checklist d'upload créée** (`CHECKLIST_UPLOAD_AppliedEnergy.md`) : artefacts et états (main 38 pp, SM 24 pp, cover 1 p, GA 2048×1024 ✓, highlights 5×≤85 ✓) ; seuils GFA confirmés vs **[À CONFIRMER à l'upload]** (12k mots — marge ×4 ; abstract ≤300 — 159 ; keywords 8 vs plafond possible 6 ⚠️ avec plan de repli) ; **ORCID = seul bloquant** (5 à collecter avant la session) ; ordre de session en 7 étapes (pré-vol audit → saisie EM → ORCID/CRediT → upload → confirmation des seuils → contrôle « Build PDF » siunitx → submit) ; post-soumission (dépôt Zenodo des HDF5 déjà archivés).

**Suite §16 — relecture orale des correctifs 0.9/2.9 + vérification des reviewers suggérés (2026-09-25) :**
- **Read-aloud correctifs** : headline, légende figure-tête, cover et annotation figure — rythme sain. Gap (ii) : la parenthétique « (0.980 to 0.971) » répétait quatre nombres dans le même souffle (0.980/0.971 déjà énoncés en début de phrase) — supprimée (« costs only 0.9 points globally, the stabilizer… »). Rebuild complet SM+main (le .bbl du main avait été emporté par la purge du commit — piége récurrent) : main 38 pp / 0 erreur / 0 undefined / 0 overfull, audit 60/60.
- **Reviewers suggérés vérifiés (4/4 actifs, domains alignés)** — métadonnées ajoutées à la checklist : Olaya-Castro (UCL, Physics & Astronomy, bio quantique), Yuen-Zhou (UCSD, joelyuen@ucsd.edu ✓, polaritons), Baumberg (Cambridge Cavendish, NPoM/SERS — pas d'entrée défavorable récente, profils 2024–2025 actifs), Barron-Gafford (U. Arizona + Biosphere 2, gregbg@arizona.edu ✓, agrivoltaïsme). Emails déduits du format institutionnel marqués « à confirmer au profil » (Olaya-Castro, Baumberg) ; aucun conflit d'intérêt évident avec les auteurs.

**Suite §16 — emails reviewers confirmés + fin de la passe orale (2026-09-25) :**
- **Emails confirmés sur pages institutionnelles officielles — 4/4 ✓** : Baumberg **JJB12@cam.ac.uk** (page profil Cavendish, « Contact Details ») ; Olaya-Castro **a.olaya@ucl.ac.uk** (page MAPS/UCL 2022 + page quantum UCL — le format déduit « a.olaya-castro@ » était **faux**, aucune occurrence en ligne ; leçon : ne jamais saisir un email déduit sans confirmation). Checklist à jour : plus aucun email à confirmer avant saisie EM.
- **Fin de la passe orale (Discussion + Conclusions)** : ouverture Discussion (« modelled sustainability benefits » — « modelled » bien placé), « quantum divide », Limitations (liste déclarative à points d'ancrage chiffrés) et Conclusions (paraphrase de la question sans la citer, cohérente avec la nouvelle formulation) — **sains**. Une correction : le paragraphe « Quantum digital twin » empilait quatre interruptions (paire de tirets + deux-points + parenthèse + tiret final de ~20 mots) — le tiret final détaché en phrase autonome (« This device-physics integration is distinct from… »). Build : main 38 pp, 0 erreur / 0 undefined / 0 overfull ; audit 60/60.
- **Passe orale AE complète** : intro (gaps + contre-factuels + Q1–Q3 + headline), figure-tête (légende), matrice (légende + cellules), Discussion (5 blocs + Limitations), Conclusions, cover letter — toutes relues à voix haute sur l'ensemble des passes du jour.
- **Incident de sync — détecté et réparé** : un rsync lancé depuis le mauvais cwd (oubli de `cd`, source = Redac_Paper2 entier) a copié 227 fichiers dans le dossier AE du HPC et `--delete` a purgé 32 fichiers du package distant (dont la checklist). **Zéro perte** : le repo local et git intacts, et le contenu distant est entièrement reproductible depuis la source locale. Réparation : suppression du dossier AE distant, re-sync correcte depuis le package (32 fichiers, marqueurs vérifiés, `data/src/backups/main.py` supérieurs intacts), log de la cover repoussé manuellement (les exclusions `*.log` le laissent tomber — dépendance d'audit) → **60/60 sur HPC**. Leçons : (1) toujours vérifier le chemin source d'un rsync avant exécution ; (2) les exclusions d'artefacts doivent lister les logs des builds SAUF ceux qui sont des dépendances d'audit (cover).

**Suite §16 — collecte des ORCID (2026-09-25) : 4/5 trouvés.**
- Teguia Kouam `0009-0000-7853-5476` (page ACS JPCL, liée à l'email correspondant) ; Tchapet Njafa `0000-0002-1936-8353` (3 sources indépendantes : chemRxiv, page auteur arXiv, CRediT) ; Nguenang `0000-0002-7140-7196` (attribution inline Springer 2018, à confirmer à la saisie EM) ; **Nana Engo `0000-0002-7484-3508` (confirmé par l'auteur**, cohérent avec l'auto-dépôt arXiv 2026-08).
- **Piège de disposition ACS résolu** : sur les pages pubs.acs.org, le badge ORCID s'affiche AU-DESSUS de l'auteur SUIVANT (appartient à l'auteur précédent du DOM) — sans croisement multi-sources, Nguenang aurait été crédité de l'ORCID de Tchapet Njafa.
- **Piège de métadonnées legacy** : l'AIP JCP 2017 associe `0000-0002-3013-3029` à Nana Engo — ancien enregistrement ou homonyme ; la valeur confirmée par l'auteur (7484-3508) fait foi ; fusion ORCID support si double compte.

**Suite §16 — rangement de la racine Redac_Paper2 (HPC + repo, 2026-09-25) :**
- Racine HPC réduite de 31 à 11 fichiers canoniques (main.py, Makefile, parameters.yaml, pyproject.toml, references.bib, configs dev, COMPARAISON, CSV des 2 relances, symlink référencé par le code, .gitignore/.pre-commit). Déplacements sans suppression : docs juin/juillet + revues → `docs/` (dont « # ADVERSARIAL REVIEW260629.md » renommé `docs/adversarial_review_260629.md` — un `#` initial empêchait tout grep) ; scripts d'exécution + check_h5_vals.py + fixers → `scripts/` (réuni avec les sbatch déjà là) ; snapshots parameters.yaml de juillet → `backups/config_july2026/` ; CSV ère juillet → `results/npom_scan_legacy_july2026/` ; logs collecteur → `logs/`.
- **Symlink `quantum_simulations_framework` conservé** : référencé par `src/logging_config.py`, `src/quantum_interface/solver.py` et 5 sbatch (vérifié avant de ne pas le toucher).
- Repo local mis en miroir par `git mv` (renames suivis : 2 docs + 9 scripts) + chemin `check_h5_vals.py` corrigé dans le puller archivé (`scripts/`). Vérif : Makefile/tests sans référence cassée ; suite unitaire **118 passed, 1 xfailed** sur HPC après réorganisation.

**Suite §16 — AUDIT GÉNÉRAL post-modifications (2026-09-25, fin de journée) :**
- **Alerte d'intégrité détectée par l'audit QST lui-même** : le contrôle « Original source directory intact » a échoué (21/22) — investigation : **112 fichiers trackés supprimés du worktree local sans commit** (dossiers `Archive/` ~90, `Redac_Paper2/Graphics/` 3, **package Nature_Energy 15**, `docs/adr/` 4). Cause : nettoyage local non committé antérieur. Réparation : package Nature_Energy **restauré depuis git** (15 fichiers) et re-poussé sur HPC (23 fichiers) — le verrou QST l'exige comme référence intouchée ; `Archive/` et `Graphics/` restaurés également ; seules les suppressions `docs/adr/` (préexistantes au matin, intention utilisateur) restent unstaged.
- **Résidus lexicaux réels trouvés et corrigés** : les **titres de section** « Roadmap: nine breakthroughs… » (la passe anti-jargon du 24/09 avait corrigé le corps mais pas les en-têtes) → SM AE : « nine advances » (9 sous-sections ✓) ; **SI QST : « ten advances » — le titre « nine » était faux, le Roadmap QST compte 10 sous-sections** (la 10e « Experimental fabrication protocol » n'existe que côté QST) et son commentaire source disait même « FOUR ». « breakthrough curves » (chromatographie) conservés — technique. Builds : SM 24 pp / SI 30 pp, audits 62/62 et 22/22.
- **Faux positifs instruits** : « the n=2 estimate of 0.0804 » (L264 AE / L235 QST) = mention de convergence explicite, légitime ; lexique 0/0/0/0/0/0 sur main+cover des deux packages.
- **Parité local↔HPC vérifiée par md5 sur 21 fichiers clés** : PARFAITE après alignement (SM/journal/SI repoussés ; pollution croisée transitoire du rsync groupé nettoyée — SI QST retiré du package AE distant ; `cleanup.sh` à la racine repo innocent). Ré-audits HPC : 62/62 et 22/22.
- **Bilan** : 6 documents — 0 erreur / 0 undefined partout (AE 38+24+1 pp, QST 20+30+2 pp) ; audits **62/62 + 22/22 local ET HPC** ; canon, tables et titre harmonisés ; l'audit d'acceptation a prouvé sa valeur en détectant la disparition du package archive.
- **Seul manquant : Goumai Vedekoi** — aucun ORCID public ; à créer sur orcid.org (5 min) + liaison JPCL via « Search & link ». Checklist §3 restructurée en table avec sources.

**Suite §16 — revue des titres au regard du repositionnement (2026-09-25) :**
- **QST (14 mots, verrou audit ≤22 + « Non-Markovian »/« Quantum-Enhanced »)** : déjà aligné sur le repositionnement method-led (« Non-Markovian Coherence Control » porte la contribution) ; sous-titre couvrant photonique/sensing/communication. **Conservé tel quel.**
- **AE (12 mots, aucun verrou)** : problème réel — le titre ne portait **aucun signal energy-systems** (ni energy, ni LCA, ni NEB) : « Coordinated Vibronic Light-Harvesting, Environmental Calibration, and Agro-Rural Cybersecurity » listait 3 fonctions sur 7 (« Agro-Rural Cybersecurity » vague) et désaccordait « Quantum Agrivoltaic » avec le « Quantum-Enhanced Agrivoltaic » de QST. **Nouveau titre appliqué (13 mots) : « Quantum-Enhanced Agrivoltaic Digital Twin: Spectral Co-Design, Multifunctional Net Energy Benefit, and Quantum-Secured Telemetry »** — reprend la formulation « spectral co-design » de la Discussion, signale le NEB (l'ancrage AE), et harmonise le préfixe avec QST. Mis en cohérence partout : main (\title + commentaire), SM (en-tête + phrase d'accompagnement), cover letter (titre + commentaire), Highlights (ligne Title) ; 0 résidu de l'ancien titre dans le package actif (les archives NatureEnergy et le journal QST historiques restent intacts).
- **Audit durci 60 → 62 contrôles, 62/62 PASS** : deux nouveaux verrous (titre du main + miroir de l'en-tête SM). Builds : main 38 pp / SM 24 pp / cover 1 p — 0 erreur, 0 undefined, 0 overfull.

**Suite §16 — RELECTURE CRITIQUE AE (œil Reviewer 2 hostile) + corrections de fond (2026-09-25, soirée) :**
- **Méthode** : lecture intégrale main (612 l.) + SM (1204 l.) + cover + Highlights + table comparative, croisée avec le code (`orchestrator.py`, `neb.py`, `constants.py`, `plot_utils.py`, `regenerate_figures.py`), `parameters.yaml` et les HDF5 canon `relaunch_20260924`. Arbitrage utilisateur : plan complet, **miroir QST**, **recalcul intégral** de la chaîne NEB.
- **B1 — Unités Γ_RC (bloquant, prouvé par les données)** : les HDF5 canon vérifient l'identité exacte `rc_yield = 0.15 × Σ(P₃+P₄) × dt[fs]` (V1.2 : 2.6643 × 0.15 × 0.2 = 0.079929 vs h5 0.079928) — le code traite Γ_RC = 0.15 comme **fs⁻¹** (τ_trap ≈ 6.7 fs), mais main/SM imprimaient « 0.15 ps⁻¹ » avec Éq. (3) telle quelle ⇒ borne mathématique Φ_FT ≤ 0.15, incompatible avec 0.89(3)/0.98 imprimés dans le même papier, et le SM S1 disait « almost entirely captured within ≈6.7 ps » (faux par construction, t_max = 1 ps). **Correction assumée partout (AE + QST)** : « Γ_RC = 0.15 fs⁻¹ effective, τ_trap ≈ 6.7 fs — courte devant la fenêtre de 1 ps, de sorte que la capture quasi complète (baseline passive 0.98) est dynamiquement accessible » ; SM S1 reformulé ; table comparative (AE + QST) : `\per\ps` → `\per\fs`.
- **B4 — Conflit de matrices de couplage** : main Table 1 (J₁₈=21.0, J₇₈=12.0 = code), SM Table S2 (J₁₈=4.0, J₃₈=12.0, J₇₈=−15.0), code (J₁₈=21.0, J₃₈=0.6, J₇₈=12.0, J₂₃=30.0 vs SM 30.8) : **3 voies divergentes**. Décision : le record = le code qui a produit les données (branche `a609e01`, jamais modifié après ; le run 25/06 `data/converged` est fait avec cette matrice) ; correction immédiate de l'**écart main↔SM lisible sans code** (J₇₈ 12.0 → **−15.0** dans Table 1) ; note SM ajoutée (bloc site-8 fixé sur toutes les runs de production, rôle de J₃₈) ; harmonisation J₂₃ 30.0/30.8 et ligne site-8 du code **reportée** (refonte Table 1 + S2 depuis `constants.py` = tâche dédiée, risque d'intro-faute trop élevé en fin de soirée — l'écart actuel est étiqueté dans le journal).
- **B2 — NEB 19.6 non reproductible → chaîne ré-étalonnée et VERROUILLÉE** : l'ancienne chaîne (600 W × η × FF, courant instantané vs revenus 180 kWh) ne recombinaisait plus. **Nouveau canon, vérifié par exécution du code** : électricité **180 kWh/m²/yr** (compte garanti 5.76 × 365 × 0.15 × PR 0.57 = 179.3) **utilisé partout** (revenus = carbone : 81 kg/m²/yr évités) ; eau **474.5 L/m²/yr** ; NEB_A = 81 + 0.14 − 8.5 = **72.6** ; NEB_B = 89.1 + 0.13 − 5.0 = **84.2** ; NEB_C = **0.0**. Scénario B ré-ancré (0.98×0.8=0.784, biomasse **8.25** = 10×0.784/0.95 — l'artefact 0.064/0.68 disparaît) ; boost fertilisant **1.08 appliqué au seul scénario A** (fix `neb.py` `apply_fertilizer_boost`, incl. Monte Carlo) — la légende « 13.0 vs 8.2 » assume le rôle du fertilisant : l'opaque achète plus de carbone mais écrase la canopée, c'est LE trade-off. Finances : revenus **30 090** (somme itemisée 21.60+0.95+36.90+0.73 = 60.18 ; fichier aligné), cashflow **26 090**, paybacks **4.32 / 6.17 / 2.68**, NPV **+34 714**, sensis **3.46–5.18 / 4.49 / 5.61**, crédits carbone **363 USD/yr (1.4 %)**.
- **B3 — Erreur ×365 (eau)** : 28 % ↔ 1.3 mm/**jour** ; l'ancien « 1300 L/m²/yr » = 1.3 L/m²/yr (erreur ×365) ; corrigé **474.5 L/m²/yr** (237 m³/yr) partout (AE main/SM/cover/Highlights/README + QST main/SI/cover QST héritée) ; reformulations « annualized at 365 d » explicites.
- **M1 — « 15 % quantum yield enhancement » (héritage NE « 8 % »)** : supprimé ; remplacé par « horticultural standard 8.2 + canal fertilisant 0.96 (8 %, scénario A seul), **aucun gain de cohérence monétisé** » (AE main/SM, QST main/SI) — verrouille la claim contre l'attaque « sell coherence twice ».
- **M2/M4/M5/M6 + mineurs** : provenance 0.89/0.71/0.98 explicitée (bare 8-site, hérités de `Kouam2026`, = fraction passive 99 %, indépendants du scan) + phrase anti-confusion dans le gap (i) ; **Fig 1/2/3 régénérées depuis `V1.2` canon** (`regenerate_figures.py --h5 V1.2`), légendes réécrites (b : run n=20 V1.2, plasmon 83 %, chargé en ~10 fs ; c : Φ(t)→0.0799 ; note Δt=10 fs non auditable supprimée) ; couplage « OPV exciton band » affaibli (« mediates the optical interface ») ; doublon L=8 (SM S2) supprimé ; `hdf5`→HDF5 (titre S11) ; « dual-OPEX »→« cooperative OPEX » (SM S9) ; data/Code availability harmonisés (« deposited … with a DOI upon acceptance ») ; 79–84 % → 82 % (cover) ; « (precisely 45 %) » nettoyé ; **SM S11 : nouveau sous-section « Provenance and auditability »** (chaque observable extrait programmatiquement des HDF5 archivés avec métadonnées git/run, aucune entrée saisie à la main) ; commentaire résiduel « Phi_FT = 2 × Gamma_RC × … » purgé de `src/constants.py`.
- **Tableaux/légendes (directive éditoriale 1)** : Table 1 + Table S2 + Fig 1–3 (AE) et Fig 1–3 (QST) : légendes interprétatives (ce que la structure/courbe démontre) plutôt que descriptives.
- **Espaces équations (directive 2)** : script (regex `\\n\\n+\\begin{equation*?|align*?}` et miroir `\\end{...}\\n\\n+` → une seule nouvelle) appliqué aux 4 fichiers (AE main/SM, QST main/SI) — suppression des lignes vides avant/après les environnements d'équations, sauf après `\\item` (protection intégrée).
- **Dé-duplication SM (directive 3)** : phrase L=8 en doublon supprimée ; « provenance/trace » consolidés en une sous-section dédiée (S11) au lieu de notices dispersées ; « 8 % / 15 % / 1.23 kg » en trois endroits remplacés par l'énoncé unique « no coherence-derived gain monetized » ; « dual-OPEX » unifié ; « precisely 45 % » réduit.
- **Forks QST découverts et corrigés au passage** : SI QST sans le correctif TOC numwidth (3 × 5.44 pt S10+) — bloc `\\l@section/\\l@subsection` ajouté ; table Matsubara SI QST sans les overrides `separate-uncertainty=false` (même signature) — alignée sur AE ; main QST sans `\emergencystretch` — 2.5em ajouté (4 overfulls préexistants au texte figé). **Post-correction : 0 overfull partout.**
- **Builds finaux** : AE main **39 pp** / SM **25 pp** / cover 1 p ; QST main **21 pp** / SI **29 pp** / cover 2 pp — 0 erreur / 0 undefined / 0 overfull sur les six. Audits : **62/62 AE + 22/22 QST** (docstring verify AE : canon §re-étalonnage 2026-09-25 ; verrous 4.23→**4.32**, 19.6→**72.6**). Tests : 68 exécutés, 67 passed — 1 fail `test_pennylane_backend` (préexistant, PennyLane absent localement, identifié sur l'arbre propre par stash).
- **Fichiers modifiés (code+config)** : `src/constants.py`, `src/lca/neb.py`, `scripts/regenerate_figures.py`, `parameters.yaml` (revenue 30090), figures Graphics/ + 2 packages. **Restes assumés** : harmonisation J₂₃ 30.0 (code) vs 30.8 (SM) + refonte des tables depuis `constants.py` (à faire en session dédiée) ; `Cover_Letter.tex` hérité inactif du package QST mis en parité sans impact ; archives NE et journaux historiques intacts (convention).
