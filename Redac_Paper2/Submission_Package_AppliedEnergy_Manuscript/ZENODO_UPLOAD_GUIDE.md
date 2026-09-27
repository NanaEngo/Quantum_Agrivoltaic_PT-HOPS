# Zenodo Upload Guide — Paper 2 Data & Code Archive

**Paper:** *Spectral Co-Design of Agrivoltaic Modules for Multifunctional Net Energy Benefit: A Quantum-Guided Digital Twin*

**Package:** `quantum_agrivoltaics_paper2_zenodo_YYYYMMDD.zip` (≈ 13 MB, 89 files)

---

## Prerequisites

- A **Zenodo account** (sign up at [zenodo.org](https://zenodo.org) — free; you can log in with ORCID, GitHub, or email)
- The built archive: `quantum_agrivoltaics_paper2_zenodo_YYYYMMDD.zip`
  - To rebuild: `bash build_zenodo_package.sh` from the submission folder

---

## Step-by-Step Upload Procedure

### Step 1 — Reserve a DOI (before journal submission)

1. Go to [zenodo.org/uploads/new](https://zenodo.org/uploads/new)
2. Click **"New Upload"**
3. **Do NOT publish yet** — just create the draft to get a reserved DOI
4. Copy the **reserved DOI** (format: `10.5281/zenodo.XXXXXXX`)
5. Paste this DOI into the manuscript's Data Availability statement:
   ```
   \subsection*{Data availability and reproducibility}
   All production trajectories, parameter files (v1.4), and analysis
   notebooks are deposited in Zenodo (DOI: 10.5281/zenodo.XXXXXXX).
   ```
6. Recompile the manuscript PDF if needed

> [!IMPORTANT]
> Reserve the DOI **before** submitting to Applied Energy. The manuscript references this DOI.
> Zenodo reserves the DOI immediately; you publish the record later (after acceptance, or at submission).

---

### Step 2 — Upload the Archive

1. On the draft upload page, drag and drop (or browse for) the file:
   ```
   quantum_agrivoltaics_paper2_zenodo_20260927.zip
   ```
2. Wait for the upload to complete (≈ 13 MB — should take < 1 minute)
3. Verify that the file appears in the "Files" section

---

### Step 3 — Fill in the Metadata

Fill each field exactly as shown below:

#### Resource Type
- **Upload type:** Dataset
- (Alternatively: "Software" if the reviewer expects code; "Dataset" is standard for combined data+code deposits)

#### Basic Information

| Field | Value |
|---|---|
| **Title** | `Data and Code for: Spectral Co-Design of Agrivoltaic Modules for Multifunctional Net Energy Benefit — A Quantum-Guided Digital Twin` |
| **Publication date** | `2026-09-27` (date of archive creation) |
| **Description** | See below |
| **Version** | `1.0.0` |

**Description** (paste this into the "Description" box):

```
Production data (HDF5 trajectories), source code (Python ≥3.12 digital-twin
framework), parameter files, figure-generation scripts, verification suite,
and LaTeX manuscript source accompanying the paper:

"Spectral Co-Design of Agrivoltaic Modules for Multifunctional Net Energy
Benefit: A Quantum-Guided Digital Twin"

by Teguia Kouam S.C., Goumai Vedekoi T., Tchapet Njafa J.-P.,
Nguenang J.-P., Nana Engo S.G.

Submitted to Applied Energy (Elsevier), September 2026.

The archive is self-contained and does not require access to any external
repository. Key results: dual-band filtered forward transfer yield
Φ_FT = 0.89 ± 0.03, global canopy yield 0.971 at 1% sentinel fraction,
NEB = 72.6 kgCO₂e/m²/yr, payback 4.32 yr (30% subsidy).

Simulation parameters: PT-HOPS/SBD, L=8, K=2, Δt=0.2 fs, T=295 K.
```

#### Authors (in order)

| Name | Affiliation | ORCID |
|---|---|---|
| Teguia Kouam, Steve Cabrel | Department of Physics, University of Douala, Cameroon | `0009-0000-7853-5476` |
| Goumai Vedekoi, Theodore | Department of Physics, University of Yaoundé I, Cameroon | *(to be created)* |
| Tchapet Njafa, Jean-Pierre | Department of Physics, University of Yaoundé I, Cameroon | `0000-0002-1936-8353` |
| Nguenang, Jean-Pierre | Department of Physics, University of Douala, Cameroon | `0000-0002-7140-7196` |
| Nana Engo, Serge Guy | Department of Physics, University of Yaoundé I, Cameroon | `0000-0002-7484-3508` |

> [!TIP]
> Enter last name first (e.g., "Teguia Kouam, Steve Cabrel"). Add ORCIDs by clicking the ORCID icon.

#### License
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- *(The LICENSE file inside the archive specifies MIT for the code; CC BY 4.0 is the Zenodo-level choice)*

#### Keywords
Enter these keywords (one per tag):
```
agrivoltaics
quantum dynamics
PT-HOPS
spectral management
net ecological benefit
FAO-56
SERS diagnostics
nanoparticle-on-mirror
techno-economic analysis
digital twin
```

#### Related Identifiers

| Relationship | Identifier |
|---|---|
| `is supplement to` | `DOI of the Applied Energy paper` (add after acceptance) |
| `is supplement to` | `10.1021/acs.jpclett.XXXXXXX` (Paper 1, JPCL — add the published DOI) |

> [!NOTE]
> Add the Applied Energy DOI once the paper is accepted and published. For now, leave a note in the "Additional notes" field: "Manuscript submitted to Applied Energy, September 2026."

#### Grants / Funding
- **Funding:** Leave empty (no specific grant; institutional support from University of Yaoundé I and University of Douala)
- Add if desired: `Additional notes: Institutional support from the University of Yaoundé I and the University of Douala. Computational resources provided by the penavoraserver cluster.`

#### Communities
- Search for and join: `energy-systems`, `quantum-biology`, `agrivoltaics` (if these communities exist on Zenodo)

---

### Step 4 — Preview and Publish

1. Click **"Preview"** to review all metadata
2. Verify:
   - [ ] Title matches the manuscript
   - [ ] All 5 authors listed with correct affiliations
   - [ ] ORCIDs attached (at least for the corresponding author)
   - [ ] Description is complete
   - [ ] License = CC BY 4.0
   - [ ] File is `quantum_agrivoltaics_paper2_zenodo_YYYYMMDD.zip`
   - [ ] Reserved DOI matches the one in the manuscript
3. Click **"Publish"**

> [!WARNING]
> **Publishing is permanent.** Once published, the DOI is minted and the record cannot be deleted (only new versions can be added). Double-check everything before clicking Publish.

---

### Step 5 — Post-Publication

1. **Copy the published DOI** (e.g., `10.5281/zenodo.12345678`)
2. **Update the manuscript** Data Availability section if the DOI changed
3. **Add the "Related identifiers"** link to the Applied Energy paper when it is published
4. **Share the DOI** with all co-authors

---

## Updating the Archive (New Version)

If you need to upload a revised version after publication:

1. Go to your published record on Zenodo
2. Click **"New version"**
3. Upload the new `.zip` file
4. Update the metadata (version number, description)
5. Publish → a new DOI is minted (the concept DOI stays the same)

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Upload fails | Check file size < 50 GB (Zenodo limit). Our archive is ≈ 13 MB. |
| Reserved DOI expired | DOI reservations on Zenodo do not expire. You can publish at any time. |
| Need to change metadata | Edit the draft before publishing, or create a new version after. |
| Reviewer asks for raw HDF5 | The HDF5 is inside the zip. Point them to `data/converged/production_dynamics.h5`. |
| LaTeX won't compile from archive | Install texlive-full; figures are in `manuscript/figures/`. The `\graphicspath` in the .tex files may need adjustment to `{figures/}`. |

---

## Summary Checklist

- [ ] Zenodo account created
- [ ] DOI reserved and pasted into manuscript
- [ ] Archive uploaded (`quantum_agrivoltaics_paper2_zenodo_YYYYMMDD.zip`)
- [ ] Metadata filled (title, authors, ORCIDs, description, license, keywords)
- [ ] Preview checked
- [ ] Published (or saved as draft pending acceptance)
- [ ] DOI shared with co-authors
- [ ] Related identifiers updated after paper acceptance
