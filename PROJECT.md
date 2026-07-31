# Project: Quantum Agrivoltaics Paper 2 QST Submission Package

## Overview
Conversion and scientific refinement of Paper 2 manuscript from Nature Energy format to IOP Quantum Science and Technology (QST) submission format (`iopart.cls`), applying all 11 corrections from `AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md`.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Duplication & Structure | Copy `Submission_Package_Nature_Energy_Manuscript/` to `Submission_Package_QST_Manuscript/` | none | DONE |
| 2 | M2: IOP iopart.cls Reformatting | Reformat MS to `iopart.cls` -> `Manuscript_QST_26-07-29.tex` | M1 | DONE |
| 3 | M3: Priority 1 Corrections | Implement F1, F4, F5, F9, F10 in MS | M2 | DONE |
| 4 | M4: Priority 2 Corrections | Implement F6, F7, F8, F11 in MS & SI | M3 | DONE |
| 5 | M5: Experimental Testability | Implement §Experimental testability (F3) | M4 | DONE |
| 6 | M6: Table 2 / Server Scan | Run n=20 scan on PenavoraServer or document n=2 note | M1 | DONE |
| 7 | M7: Final Compilation & Cover Letter | Compile PDF, update SI header, generate Cover Letter, run verification | M5, M6 | DONE |

## Interface Contracts & Layout
- Target Directory: `Redac_Paper2/Submission_Package_QST_Manuscript/`
- Files: `Manuscript_QST_26-07-29.tex`, `SI.tex`, `Cover_Letter_QST.tex`, `references.bib`, `iopart.cls`, `Figures/`
