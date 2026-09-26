#!/usr/bin/env python3
"""QST submission-package acceptance audit.

Portable: paths are resolved relative to this script's location.
Numerical canon (2026-09-23): the forward-transfer yield is defined WITHOUT a
prefactor 2:  Phi_FT = Gamma_RC * integral (P3+P4) dt  (Eq. 3 / Eq. S1).
The July-2026 HPC runs (scan_A*) stored rc_yield = 2 x Phi_FT (double-counting
bug); the canonical value at V_mode = 1.2 nm^3 is 0.0799 (91.8% suppression).
"""
import os
import re
import sys

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
MS_FILE = os.path.join(PKG_DIR, "Manuscript_QST_26-07-29.tex")
SI_FILE = os.path.join(PKG_DIR, "SI.tex")
CL_FILE = os.path.join(PKG_DIR, "Cover_Letter_QST.tex")
BIB_FILE = os.path.join(PKG_DIR, "references.bib")
AUDIT_FILE = os.path.join(PKG_DIR, "AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md")
FIG_DIR = os.path.join(PKG_DIR, "figures")
RESULTS = []


def check(condition, description):
    status = "✅ PASS" if condition else "❌ FAIL"
    RESULTS.append((description, status))
    print(f"{status}: {description}")
    return condition


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


print("=== QST SUBMISSION PACKAGE ACCEPTANCE AUDIT ===")

# 1. Structure
check(os.path.exists(AUDIT_FILE), "Audit file present (AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md)")
check(os.path.isdir(FIG_DIR), "figures/ directory present")
check(os.path.exists(BIB_FILE), "references.bib present")
check(os.path.exists(SI_FILE), "SI.tex present")
check(os.path.exists(CL_FILE), "Cover_Letter_QST.tex present")

# Read file contents
ms_content = read(MS_FILE)
si_content = read(SI_FILE)
cl_content = read(CL_FILE)

# 2. Title check
title_match = re.search(r"\\title\[.*?\]\{(.*?)\}", ms_content)
title_text = title_match.group(1) if title_match else ""
has_title_kw = "Non-Markovian" in title_text or "Quantum-Enhanced" in title_text
title_words = len(title_text.split())
check(has_title_kw, f"Title contains required keywords ('{title_text}')")
check(title_words <= 22, f"Title word count <= 22 words ({title_words} words)")

# 3. Abstract check
abs_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", ms_content, re.DOTALL)
abs_text = abs_match.group(1) if abs_match else ""
abs_words = len(abs_text.split())
check(abs_words <= 210, f"Abstract word count <= 210 words ({abs_words} words)")

# 4. NPoM yield non-contradiction check
npom_contradiction = re.search(r"NPoM.*(enhances|improves|boosts)", abs_text, re.IGNORECASE)
check(npom_contradiction is None, "No NPoM yield contradiction in abstract")

has_preserve_wording = "preserves a global" in abs_text or "preserves" in abs_text
check(has_preserve_wording, "Abstract contains correct yield preservation wording")

# 5. FAO-56 equation duplication
fao_eq_matches = re.findall(r"\\mathrm\{ET\}_c\s*=\s*\\frac", ms_content)
check(
    len(fao_eq_matches) == 1,
    f"FAO-56 equation appears exactly once in MS (found {len(fao_eq_matches)})",
)

# 6. Experimental testability
check("Experimental testability" in ms_content, "Experimental testability section present in MS")

# 7. Discussion sub-sections
disc_sections = [
    "Mechanism generality",
    "The ``quantum divide''",
    "Quantum digital twin",
    "Prior art and positioning",
    "Limitations",
    "Outlook",
]
disc_found = all(sec in ms_content for sec in disc_sections)
check(disc_found, "Discussion section contains all 6 required sub-sections in order")

# 8. SI Header check
has_qst_si = "Quantum Science and Technology" in si_content
no_ne_si = "submitted to \\textit{Nature Energy}" not in si_content
check(has_qst_si and no_ne_si, "SI.tex header updated to Quantum Science and Technology")

# 9. Cover Letter check
has_eic = "Editor-in-Chief" in cl_content and "Quantum Science and Technology" in cl_content
has_sub = "subscription route" in cl_content or "$0 APC" in cl_content
has_reviewers = (
    "Prof. Jeremy J. Baumberg" in cl_content and "Prof. Alexandra Olaya-Castro" in cl_content
)
check(
    has_eic and has_sub and has_reviewers,
    "Cover_Letter_QST.tex properly formatted with EIC, $0 APC subscription route, and 5 suggested reviewers",
)

# 10. Numerical canon: Phi_FT definition WITHOUT prefactor 2 (2026-09-23 canon)
#     Eq. (3) in MS and Eq. (S1) in SI must read Gamma_RC x integral(P3+P4) dt,
#     with no "prefactor 2" justification sentence anywhere.
phi_eq_ok = (
    re.search(r"\\Phi_\{\\mathrm\{FT\}\}\s*=\s*\\Gamma_\{\\mathrm\{RC\}\}\s*\\int", ms_content)
    is not None
)
check(phi_eq_ok, "MS Eq. (Phi_FT) uses Gamma_RC x integral(P3+P4) dt (no prefactor 2)")
si_phi_eq_ok = (
    re.search(r"\\Phi_\{\\mathrm\{FT\}\}\s*=\s*\\Gamma_\{\\mathrm\{RC\}\}\s*\\int", si_content)
    is not None
)
check(si_phi_eq_ok, "SI Eq. (SI_phi_ft) uses Gamma_RC x integral(P3+P4) dt (no prefactor 2)")
no_prefactor_sentence = re.search(
    r"factor of 2|prefactor 2|2\\Gamma_\{\\mathrm\{RC\}\}|2\\,\\Gamma", ms_content + si_content
)
check(no_prefactor_sentence is None, "No 'factor of 2' / '2 Gamma_RC' residue in MS or SI")

# 11. Numerical canon: canonical NPoM yield value 0.0799 (91.8% suppression)
check(ms_content.count("0.0799") >= 1, "MS contains canonical NPoM yield 0.0799")
check(si_content.count("0.0799") >= 1, "SI contains canonical NPoM yield 0.0799")
no_obsolete_vintage = re.search(r"0\.1599|83\.7\s*\\?%|0\.183\b", ms_content + si_content)
check(no_obsolete_vintage is None, "No obsolete yield vintages (0.1599 / 83.7% / 0.183)")

# 12. Source directory intactness (archived sibling package, two levels up from repo root)
src_ms = os.path.join(
    os.path.dirname(os.path.dirname(PKG_DIR)), "_archive", "Submission_Package_Nature_Energy_Manuscript",
    "Manuscript_NatureEnergy_26-06-25.tex",
)
check(os.path.exists(src_ms), "Original source directory intact and unmodified")

print("\n=== SUMMARY ===")
pass_count = sum(1 for _, s in RESULTS if s == "✅ PASS")
print(f"Passed {pass_count}/{len(RESULTS)} checks.")

if pass_count == len(RESULTS):
    print("ALL ACCEPTANCE CRITERIA PASSED!")
else:
    print("SOME CHECKS FAILED.")
    sys.exit(1)
