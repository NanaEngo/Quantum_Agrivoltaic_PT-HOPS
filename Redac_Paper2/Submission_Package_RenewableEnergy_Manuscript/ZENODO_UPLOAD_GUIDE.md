# Zenodo & Editorial Manager Metadata Guide — Paper 2 (*Renewable Energy*)

**Manuscript:** *Semi-Transparent Organic Agrivoltaics for Cameroonian Perennial Crops: Seasonal Shade Response, Cooperative Techno-Economics, and a Bound on Quantum-Coherence Effects*

**Target Journal:** *Renewable Energy* (Elsevier, ISSN 0960-1481)

**Working Package:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/` (`parameters.yaml` `framework_version: 2.5.0`)

---

## 1. Author Roster, Affiliations & ORCID iDs

Use this table identically for **Editorial Manager** author entry and **Zenodo** contributor metadata:

| Order | Name (`Family, Given`) | Affiliation | ORCID iD | Role |
|---|---|---|---|---|
| 1 | `Teguia Kouam, Steve Cabrel` | Department of Physics, Faculty of Science, University of Douala, P.O. Box 24157, Douala, Cameroon | `0009-0000-7853-5476` | First author |
| 2 | `Goumai Vedekoi, Theodore` | Department of Physics, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon | *(not yet registered in workspace)* | Co-author |
| 3 | `Tchapet Njafa, Jean-Pierre` | Department of Physics, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon | `0000-0002-1936-8353` | Co-author |
| 4 | `Nguenang, Jean-Pierre` | Department of Physics, Faculty of Science, University of Douala, P.O. Box 24157, Douala, Cameroon | `0000-0002-7140-7196` | Co-author |
| 5 | `Nana Engo, Serge Guy` | Department of Physics, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon | `0000-0002-7484-3508` | **Corresponding author** (`serge.nana-engo@facsciences-uy1.cm`) |

---

## 2. Zenodo Deposit Metadata (`zenodo.org`)

### Step 1 — Reserve a DOI before Journal Upload

1. Sign in at [zenodo.org/uploads/new](https://zenodo.org/uploads/new) and click **New Upload**.
2. Reserve a DOI (`10.5281/zenodo.XXXXXXX`) **before** publishing.
3. Add the reserved DOI to the `Data availability` section of `RENE_main_2611.tex` (currently archival prose referencing the Supporting Material) and recompile before final portal submission if depositing publicly at submission.

### Step 2 — Bundle Verification & Packaging

Run from `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`:

```bash
make check test PYTHON=/home/taamangtchu/miniforge3/envs/qom/bin/python
python3 scripts/make_release_manifest.py
```

Package clean source, scripts, `data/`, `figures/`, `parameters.yaml`, `references.bib`, and compiled PDFs (excluding LaTeX build auxiliaries `*.aux`, `*.log`, `*.out`, `*.spl`, `*.bbl`, `*.blg`) or run `make clean` before archiving.

### Step 3 — Zenodo Fields

- **Resource type:** `Dataset` (combined data, scripts, and reproduction suite)
- **Title:** `Data and Code for: Semi-Transparent Organic Agrivoltaics for Cameroonian Perennial Crops: Seasonal Shade Response, Cooperative Techno-Economics, and a Bound on Quantum-Coherence Effects`
- **Version:** `2.5.0` (matches `parameters.yaml`)
- **License:** `Creative Commons Attribution 4.0 International (CC BY 4.0)`
- **Keywords:**
  `PM6:Y6 transfer-matrix optics`, `Cameroon highlands`, `Penja white pepper`, `wet-dry regime inversion`, `environmental carbon payback`, `Sobol global sensitivity`, `agrivoltaics`, `FAO-56`, `open quantum systems`
- **Funding / Grants:** Leave empty (*This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors; no institutional support from Universities of Yaoundé I or Douala claimed. Computational resources were provided by the penavoraserver cluster through Penabei Samafou.*)

#### Description Template

```text
Self-contained data, parameter ledger (parameters.yaml v2.5.0), transfer-matrix
optical spectra, 14-site LHCII open-quantum steady-state and MesoHOPS/HEOM
bounds, ERA5 2014-2023 hourly microclimate/FvCB/FAO-56 outputs, cooperative TEA/LCA/Sobol
scripts, verification test suite, and LaTeX manuscript sources accompanying:

"Semi-Transparent Organic Agrivoltaics for Cameroonian Perennial Crops: Seasonal
Shade Response, Cooperative Techno-Economics, and a Bound on Quantum-Coherence Effects"

by S. C. Teguia Kouam, T. Goumai Vedekoi, J.-P. Tchapet Njafa, J.-P. Nguenang,
and S. G. Nana Engo (submitted to Renewable Energy, Elsevier).
```

#### Related Identifiers

| Relationship | Identifier |
|---|---|
| `is supplement to` | *(DOI of the published Renewable Energy article once assigned)* |
| `references` | *(Paper 1 JPCL DOI, Manuscript ID `jz-2026-00994t`, once added)* |

---

## 3. Editorial Manager Pre-Upload Summary

- **Manuscript (`RENE_main_2611.pdf` / `.tex`)**: Original Research Paper (`20` pages, `4,705` prose words / `5,194` incl. captions, `50` references; compiles with `elsarticle` + `RENE_SM_2611` cross-references).
- **Supporting Material (`RENE_SM_2611.pdf` / `.tex`)**: Supplementary files §S1–S9 (`13` pages, `21` references).
- **Graphical Abstract (`figures/Graphical_Abstract_RENE_2611.png` / `.pdf`)**: Landscape 3-panel summary (`3590 x 1315 px` @ `300 DPI`, exceeding Elsevier's `>= 1328 x 531 px` floor).
- **Cover Letter (`RENE_Cover_letter_2611.pdf`)** and **Highlights (`RENE_Highlights_2611.txt` / `.tex`)**: Separate upload files (`5` bullets, `<= 85` chars per bullet).
- **Funding statement**: Explicit no-grant / no-funding declaration (matching `RENE_main_2611.tex`).
- **Pre-upload reminder**: Add `T. Goumai Vedekoi`'s ORCID iD if registered before submission.
