#!/usr/bin/env python3
"""Applied Energy submission-package acceptance audit.

Portable: paths are resolved relative to this script's location.
Numerical canon (2026-09-23): Phi_FT = Gamma_RC * integral(P3+P4) dt, WITHOUT
a prefactor 2 (Eq. 3 / Eq. S1). Canonical NPoM yield at V_mode = 1.2 nm^3 is
0.0799 (91.8% suppression); global canopy yield 0.971; payback 4.32 yr.
Economic chain re-derived 2026-09-25 (critical review): Gamma_RC = 0.15 fs-1
effective (tau_trap ~ 6.7 fs); water credit 460 L/m2/yr (1.26 mm/day x 365 =
459.9 L, from ET open 4.50 - shield 3.24 mm/day at Rn = 14.05 MJ/m2/day,
f_shade = GCR(1 - tau_AVT) = 0.55 x 0.75 = 0.41); unified electricity account
180 kWh/m2/yr (guaranteed yield); NEB_A = 72.6 kgCO2e/m2/yr (81 - 8.5 + 0.14);
NEB_B = 84.2; Scenario B biomass = 8.2 (0.8 x 0.98/0.95); revenue 30075 USD;
paybacks 4.32 / 6.17 / 2.68 yr; NPV +34630 USD; carbon credits 363 USD/yr.
Framing canon (2026-09-24): three literature gaps (static optics / TEA-LCA
decoupled / sensing bolted on) with quantified counterfactual costs, three
firsts, falsifiable claims F1-F3, deployment barriers split economic
(tractable) vs physical.
Novelty canon (2026-09-25): one-sentence central question with three
subordinate questions Q1-Q3 mapped to Results; capability matrix
(tab:capability_matrix); head figure fig:flat_canopy (local quenching vs
flat canopy plateau).
"""
import os
import re
import sys

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
MS_FILE = os.path.join(PKG_DIR, "AppliedEnergy_main_2609.tex")
SI_FILE = os.path.join(PKG_DIR, "AppliedEnergy_SM_2609.tex")
CL_FILE = os.path.join(PKG_DIR, "AppliedEnergy_Cover_letter.tex")
HL_FILE = os.path.join(PKG_DIR, "Highlights_AppliedEnergy.txt")
BIB_FILE = os.path.join(PKG_DIR, "references.bib")
README_FILE = os.path.join(PKG_DIR, "README_AppliedEnergy.md")
GA_FILE = os.path.join(PKG_DIR, "figures", "Graphical_Abstract_wide.png")
RESULTS = []


def check(condition, description):
    status = "✅ PASS" if condition else "❌ FAIL"
    RESULTS.append((description, status))
    print(f"{status}: {description}")
    return condition


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


print("=== APPLIED ENERGY SUBMISSION PACKAGE ACCEPTANCE AUDIT ===")

# 1. Package completeness
check(os.path.exists(MS_FILE), "AppliedEnergy_main_2609.tex present")
check(os.path.exists(SI_FILE), "SI.tex present")
check(os.path.exists(CL_FILE), "AppliedEnergy_Cover_letter.tex present")
check(os.path.exists(HL_FILE), "Highlights_AppliedEnergy.txt present")
check(os.path.exists(BIB_FILE), "references.bib present")
check(os.path.exists(README_FILE), "README_AppliedEnergy.md present")
check(os.path.exists(GA_FILE), "Graphical abstract (figures/Graphical_Abstract_wide.png) present")

ms_content = read(MS_FILE)
si_content = read(SI_FILE)
cl_content = read(CL_FILE)
hl_content = read(HL_FILE)
bib_content = read(BIB_FILE)

# 2. Elsevier structure
check("\\documentclass[preprint,12pt]{elsarticle}" in ms_content, "elsarticle class (preprint, 12pt)")
check("elsarticle-num" in ms_content, "Numbered bibliography (elsarticle-num)")
for sec in [
    "CRediT authorship contribution statement",
    "Declaration of competing interest",
    "Declaration of generative AI",
    "Data availability",
    "Nomenclature",
]:
    check(sec in ms_content, f"Elsevier-required section present: {sec}")

# 3. SI terminology (Elsevier: "Supplementary Material", not "Supporting Information")
check("Supplementary Material" in si_content, "SI retitled 'Supplementary Material' (Elsevier terminology)")
check("Supporting Information" not in si_content, "No 'Supporting Information' residue in SI")

# 4. Abstract and keywords (AE: <=300 words, 6-8 keywords)
abs_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", ms_content, re.DOTALL)
abs_text = abs_match.group(1) if abs_match else ""
abs_words = len(abs_text.split())
check(abs_words <= 300, f"Abstract word count <= 300 ({abs_words} words)")
kw_match = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", ms_content, re.DOTALL)
n_kw = kw_match.group(1).count("\\sep") + 1 if kw_match else 0
# Tolerant range: the exact cap is not confirmed from the official GFA (403 at
# audit time) — verify against Editorial Manager at upload.
check(5 <= n_kw <= 8, f"Keywords count 5-8 ({n_kw} keywords — confirm official cap at upload)")

# 5. Highlights: 5 bullets, <=85 characters each
bullets = [ln[2:].strip() for ln in hl_content.splitlines() if ln.startswith("- ")]
check(len(bullets) == 5, f"Highlights: exactly 5 bullets ({len(bullets)})")
max_len = max((len(b) for b in bullets), default=0)
check(max_len <= 85, f"Highlights: all bullets <= 85 chars (max {max_len})")
check(any("First quantum-coherence-guided" in b for b in bullets),
      "Highlights carry the first-of-kind claim (no AES-256 filler)")
check(not any("AES-256" in b for b in bullets), "No 'AES-256' residue in highlights")

# 6. Cover letter: AE Guide for Authors questions
cl_checks = {
    "novelty statement": "Novelty, compliance, and declarations" in cl_content,
    "audience/fit (Why Applied Energy)": "Why \\textit{Applied Energy}?" in cl_content,
    "significance": "Significance of the work" in cl_content,
    "native-speaker check": "native English speaker" in cl_content,
    "reviewer availability": "available to review" in cl_content,
    "not under consideration elsewhere": "not under consideration elsewhere" in cl_content,
}
for desc, ok in cl_checks.items():
    check(ok, f"Cover letter: {desc}")
# Real single-page check: parsed from the pdflatex build log artifact.
cl_log = os.path.join(PKG_DIR, "AppliedEnergy_Cover_letter.log")
if os.path.exists(cl_log):
    cl_pages = re.search(r"Output written on .*\((\d+) page", read(cl_log))
    found = cl_pages.group(1) if cl_pages else "?"
    check(found == "1", f"Cover letter builds to exactly 1 page ({found} found)")
else:
    check(False, "Cover letter build log absent — rebuild before auditing page count")

# 6b. AE-specific items screened at triage
check("\\linenumbers" in ms_content, "Line numbering enabled for review (\\linenumbers)")

# Word limit (~12,000 excluding references/captions — secondary-source figure;
# confirm against the official Guide for Authors at upload). Crude de-TeX count.
ms_body = ms_content.split("\\begin{document}", 1)[-1]
for marker in ("\\bibliographystyle", "\\section*{Acknowledgements}"):
    ms_body = ms_body.split(marker, 1)[0]
ms_body = re.sub(r"%.*", "", ms_body)
ms_body = re.sub(r"\\begin\{(equation|align|eqnarray|table|table\*|figure|figure\*)\}.*?\\end\{\1\}", " ", ms_body, flags=re.DOTALL)
ms_body = re.sub(r"\$[^$]*\$", " QTY ", ms_body)
ms_body = re.sub(r"\\[a-zA-Z]+(\[[^\]]*\])?(\{[^{}]*\})*", " ", ms_body)
ms_body = re.sub(r"[{}\\~]", " ", ms_body)
ms_words = len([w for w in ms_body.split() if any(c.isalnum() for c in w)])
check(ms_words <= 12000, f"Main word count <= 12,000 excl. refs/captions (~{ms_words} words, crude de-TeX)")

# At least 2 cited Applied Energy papers (editorial fit signal)
ae_keys = []
for entry in bib_content.split("@")[1:]:
    if "{" not in entry:
        continue
    key = entry.split("{", 1)[1].split(",", 1)[0].strip()
    if re.search(r"journal\s*=\s*\{[^}]*Applied Energy", entry):
        ae_keys.append(key)
ae_cited = [k for k in ae_keys if re.search(r"\\cite\{[^}]*\b" + re.escape(k) + r"\b", ms_content)]
check(len(ae_cited) >= 2, f"At least 2 Applied Energy papers cited ({len(ae_cited)}: {', '.join(ae_cited[:4])})")

# Graphical abstract dimensions (README: 2048x1024 AE-compliant wide canvas)
def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")

ga_size = png_size(GA_FILE)
check(ga_size == (2048, 1024), f"Graphical abstract is 2048x1024 (found {ga_size})")

# 7. Numerical canon: Phi_FT definition WITHOUT prefactor 2 (2026-09-23)
phi_eq_ok = (
    re.search(r"\\Phi_\{\\mathrm\{FT\}\}\s*=\s*\\Gamma_\{\\mathrm\{RC\}\}\s*\\int", ms_content)
    is not None
)
check(phi_eq_ok, "MS Eq. (Phi_FT) uses Gamma_RC x integral(P3+P4) dt (no prefactor 2)")
si_phi_eq_ok = (
    re.search(r"\\Phi_\{\\mathrm\{FT\}\}\s*=\s*\\Gamma_\{\\mathrm\{RC\}\}\s*\\int", si_content)
    is not None
)
check(si_phi_eq_ok, "SI Eq. (Phi_FT) uses Gamma_RC x integral(P3+P4) dt (no prefactor 2)")
no_prefactor_sentence = re.search(
    r"factor of 2|prefactor 2|2\\Gamma_\{\\mathrm\{RC\}\}|2\\,\\Gamma", ms_content + si_content
)
check(no_prefactor_sentence is None, "No 'factor of 2' / '2 Gamma_RC' residue in MS or SI")

# 8. Numerical canon: values
check(ms_content.count("0.0799") >= 1, "MS contains canonical NPoM yield 0.0799")
check(si_content.count("0.0799") >= 1, "SI contains canonical NPoM yield 0.0799")
no_obsolete_vintage = re.search(r"0\.1599|83\.7\s*\\?%|0\.183\b", ms_content + si_content)
check(no_obsolete_vintage is None, "No obsolete vintage (0.1599 / 83.7% / 0.183)")
for val, desc in [("0.971", "global canopy yield 0.971"), ("91.8", "suppression 91.8%"),
                  ("4.32", "payback 4.32 yr"), ("72.6", "NEB 72.6 kgCO2e/m2/yr")]:
    check(val in ms_content, f"MS contains {desc}")
check(all(v in ms_content for v in ["0.0505", "0.0605", "0.0727", "0.0768"]),
      "MS scan table carries the canonical series (0.0505/0.0605/0.0727 + n=100 ref 0.0768)")

# 9. Framing canon (2026-09-24): gaps / central question / claims / firsts / barriers
check("three gaps recur" in ms_content, "Intro states three recurring literature gaps")
check("The optical architecture is \\emph{static}" in ms_content,
      "Gap (i): static optical architecture formulation present")
check("decoupled from the underlying device physics" in ms_content,
      "Gap (ii): TEA/LCA decoupled from device physics formulation present")
check("treated purely as an energy harvester" in ms_content,
      "Gap (iii): PV as pure energy harvester (sensing bolted on) formulation present")
check("The central question of this work is falsifiable" in ms_content,
      "Central question explicitly stated as falsifiable (one sentence)")
check(all(f in ms_content for f in ["(Q1) Device", "(Q2) Physics", "(Q3) System"]),
      "Three subordinate questions Q1-Q3 mapped to Results")
check("tab:capability_matrix" in ms_content and "Multifunctional accounting" in ms_content,
      "Capability matrix present (7 functions x 4 classes)")
check("fig:flat_canopy" in ms_content and "Figure_Plateau_Canopy.png" in ms_content,
      "Head figure fig:flat_canopy (local quenching vs flat canopy) present")
check("Quantum-Enhanced Agrivoltaic Digital Twin: Spectral Co-Design, Multifunctional Net Energy Benefit" in ms_content,
      "MS title carries the energy-systems signal (title review 2026-09-25)")
check("Quantum-Enhanced Agrivoltaic Digital Twin: Spectral Co-Design, Multifunctional Net Energy Benefit" in si_content,
      "SM header mirrors the reviewed title")
check("factor of 1.6 and the SERS enhancement by a factor of 48" in ms_content
      and "costs only 0.9 points globally" in ms_content
      and "canopy-yield cost of \\qty{0.9}{\\percent}" in ms_content
      and "0.9-point canopy-scale cost" in ms_content,
      "Quantified counterfactual costs present in the three gaps (0.9-pt NPoM cost vs 2.9-pt ideal shortfall)")
check(all(f in ms_content for f in ["(F1) Microscopic", "(F2) Device", "(F3) System"]),
      "Three falsifiable claim families F1/F2/F3 present")
check("the first (i)" in ms_content and "and (iii)" in ms_content,
      "Discussion positions the three firsts (first (i)...(iii))")
check("three firsts" in cl_content or "we report the first (i)" in cl_content,
      "Cover letter mirrors the three-firsts novelty claim")
check("physical rather than economic" in ms_content,
      "Conclusions split deployment barriers: physical vs economic")
check("Deployment barriers are made explicit" in cl_content,
      "Cover letter states the economic-vs-physical barrier split")
check("KaurJeet2026" in ms_content and "KaurJeet2026" in bib_content,
      "New 2026 quantum-sensing-in-agriculture reference cited (KaurJeet2026)")
check("unreported" in cl_content, "Cover letter keeps the bounded 'to our knowledge, unreported' wording")

# Summary
n_pass = sum(1 for _, s in RESULTS if s.startswith("✅"))
n_fail = len(RESULTS) - n_pass
print(f"\n=== SUMMARY: {n_pass}/{len(RESULTS)} checks PASS, {n_fail} FAIL ===")
sys.exit(0 if n_fail == 0 else 1)
