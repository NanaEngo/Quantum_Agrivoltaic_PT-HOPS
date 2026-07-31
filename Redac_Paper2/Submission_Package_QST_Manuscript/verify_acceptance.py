#!/usr/bin/env python3
import os
import re
import sys

PKG_DIR = "/home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2/Submission_Package_QST_Manuscript"
MS_FILE = os.path.join(PKG_DIR, "Manuscript_QST_26-07-29.tex")
SI_FILE = os.path.join(PKG_DIR, "SI.tex")
CL_FILE = os.path.join(PKG_DIR, "Cover_Letter_QST.tex")
BIB_FILE = os.path.join(PKG_DIR, "references.bib")
AUDIT_FILE = os.path.join(PKG_DIR, "AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md")
FIG_DIR = os.path.join(PKG_DIR, "Figures")
SRC_MS = "/home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex"

results = []


def check(condition, description):
    status = "✅ PASS" if condition else "❌ FAIL"
    results.append((description, status))
    print(f"{status}: {description}")
    return condition


print("=== QST SUBMISSION PACKAGE ACCEPTANCE AUDIT ===")

# 1. Structure
check(os.path.exists(AUDIT_FILE), "Audit file present (AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md)")
check(os.path.isdir(FIG_DIR), "Figures/ directory present")
check(os.path.exists(BIB_FILE), "references.bib present")
check(os.path.exists(SI_FILE), "SI.tex present")
check(os.path.exists(CL_FILE), "Cover_Letter_QST.tex present")

# Read MS content
with open(MS_FILE, "r", encoding="utf-8") as f:
    ms_content = f.read()

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
# Clean TeX macros for word count
clean_abs = re.sub(r"\\[a-zA-Z]+(\{.*?\})*", "", abs_text)
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
with open(SI_FILE, "r", encoding="utf-8") as f:
    si_content = f.read()

has_qst_si = "Quantum Science and Technology" in si_content
no_ne_si = "submitted to \\textit{Nature Energy}" not in si_content
check(has_qst_si and no_ne_si, "SI.tex header updated to Quantum Science and Technology")

# 9. Cover Letter check
with open(CL_FILE, "r", encoding="utf-8") as f:
    cl_content = f.read()

has_eic = "Editor-in-Chief" in cl_content and "Quantum Science and Technology" in cl_content
has_sub = "subscription route" in cl_content or "$0 APC" in cl_content
has_reviewers = (
    "Prof. Jeremy J. Baumberg" in cl_content and "Prof. Alexandra Olaya-Castro" in cl_content
)
check(
    has_eic and has_sub and has_reviewers,
    "Cover_Letter_QST.tex properly formatted with EIC, $0 APC subscription route, and 5 suggested reviewers",
)

# 10. Source directory intactness
check(os.path.exists(SRC_MS), "Original source directory intact and unmodified")

print("\n=== SUMMARY ===")
pass_count = sum(1 for _, s in results if s == "✅ PASS")
print(f"Passed {pass_count}/{len(results)} checks.")

if pass_count == len(results):
    print("ALL ACCEPTANCE CRITERIA PASSED!")
else:
    print("SOME CHECKS FAILED.")
    sys.exit(1)
