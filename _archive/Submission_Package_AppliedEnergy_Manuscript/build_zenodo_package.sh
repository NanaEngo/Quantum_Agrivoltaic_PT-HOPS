#!/usr/bin/env bash
# =============================================================================
# build_zenodo_package.sh
#
# Assembles a self-contained Zenodo archive for Paper 2:
#   "Spectral Co-Design of Agrivoltaic Modules for Multifunctional Net Energy
#    Benefit: A Quantum-Guided Digital Twin"
#
# The resulting archive must NOT depend on GitHub — everything is embedded.
#
# Usage:  bash build_zenodo_package.sh
# Output: zenodo_package/  directory + quantum_agrivoltaics_paper2_zenodo_YYYYMMDD.zip
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAPER2_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ZENODO_DIR="$SCRIPT_DIR/zenodo_package"
TIMESTAMP=$(date +%Y%m%d)

echo "=== Building Zenodo package ==="
echo "Paper2 root : $PAPER2_ROOT"
echo "Output dir  : $ZENODO_DIR"

# Clean previous build
rm -rf "$ZENODO_DIR"
mkdir -p "$ZENODO_DIR"

# ---- 1. Source code (digital-twin framework) ----
echo "[1/8] Copying source code..."
cp -r "$PAPER2_ROOT/src" "$ZENODO_DIR/src"
cp "$PAPER2_ROOT/main.py" "$ZENODO_DIR/main.py"
cp "$PAPER2_ROOT/pyproject.toml" "$ZENODO_DIR/pyproject.toml"

# ---- 2. Parameters (single source of truth) ----
echo "[2/8] Copying parameters..."
cp "$PAPER2_ROOT/parameters.yaml" "$ZENODO_DIR/parameters.yaml"

# ---- 3. Production data (HDF5) ----
echo "[3/8] Copying production data..."
mkdir -p "$ZENODO_DIR/data/converged"
cp "$PAPER2_ROOT/data/converged/production_dynamics.h5" "$ZENODO_DIR/data/converged/production_dynamics.h5"

# ---- 4. Scripts (figure generation, table extraction, production launch) ----
echo "[4/8] Copying scripts..."
cp -r "$PAPER2_ROOT/scripts" "$ZENODO_DIR/scripts"
# Also copy figure-generation scripts from the submission folder
for f in plot_si_figures.py plot_plateau_canopy.py; do
    if [ -f "$SCRIPT_DIR/$f" ]; then
        cp "$SCRIPT_DIR/$f" "$ZENODO_DIR/scripts/$f"
    fi
done

# ---- 5. Tests ----
echo "[5/8] Copying tests..."
cp -r "$PAPER2_ROOT/tests" "$ZENODO_DIR/tests"

# ---- 6. Manuscript LaTeX source + figures ----
echo "[6/8] Copying manuscript LaTeX and figures..."
mkdir -p "$ZENODO_DIR/manuscript/figures"
cp "$SCRIPT_DIR/AppliedEnergy_main_2609.tex" "$ZENODO_DIR/manuscript/"
cp "$SCRIPT_DIR/AppliedEnergy_SM_2609.tex" "$ZENODO_DIR/manuscript/"
cp "$SCRIPT_DIR/AppliedEnergy_Cover_letter.tex" "$ZENODO_DIR/manuscript/"
cp "$SCRIPT_DIR/AppliedEnergy_Highlights_2609.tex" "$ZENODO_DIR/manuscript/"
cp "$SCRIPT_DIR/Highlights_AppliedEnergy.txt" "$ZENODO_DIR/manuscript/"
cp "$SCRIPT_DIR/references.bib" "$ZENODO_DIR/manuscript/"
cp "$SCRIPT_DIR/table_comparative_4runs.tex" "$ZENODO_DIR/manuscript/"
# Figures (main + SI + graphical abstract)
cp "$SCRIPT_DIR/figures/"*.png "$ZENODO_DIR/manuscript/figures/"

# ---- 7. Compiled PDFs (for immediate readability) ----
echo "[7/8] Copying compiled PDFs..."
for pdf in AppliedEnergy_main_2609.pdf AppliedEnergy_SM_2609.pdf AppliedEnergy_Cover_letter.pdf; do
    if [ -f "$SCRIPT_DIR/$pdf" ]; then
        cp "$SCRIPT_DIR/$pdf" "$ZENODO_DIR/manuscript/$pdf"
    fi
done

# ---- 8. Verification script ----
echo "[8/8] Copying verification script..."
cp "$SCRIPT_DIR/verify_acceptance.py" "$ZENODO_DIR/scripts/verify_acceptance.py"

# ---- 9. README and LICENSE ----
echo "[9/9] Creating README and LICENSE..."
# These are generated inline so the package is always self-consistent.
# The README content is maintained in build_zenodo_package.sh for single-source control.
cat > "$ZENODO_DIR/LICENSE" << 'LICEOF'
===============================================================================
LICENSE — Quantum Agrivoltaics Paper 2 Archive
===============================================================================

This archive contains both DATA/MANUSCRIPT and SOURCE CODE components,
each under a different license.

-------------------------------------------------------------------------------
1. DATA, FIGURES, AND MANUSCRIPT (CC BY 4.0)
-------------------------------------------------------------------------------

Files in: data/, manuscript/, and all .png, .pdf, .tex, .bib files.

Creative Commons Attribution 4.0 International License (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

You are free to share and adapt the material for any purpose, even
commercially, under the following terms:
  - Attribution: You must give appropriate credit, provide a link to the
    license, and indicate if changes were made.

-------------------------------------------------------------------------------
2. SOURCE CODE (MIT License)
-------------------------------------------------------------------------------

Files in: src/, scripts/, tests/, main.py, pyproject.toml, parameters.yaml

MIT License

Copyright (c) 2026 Teguia Kouam S.C., Goumai Vedekoi T., Tchapet Njafa J.-P.,
Nguenang J.-P., Nana Engo S.G.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
===============================================================================
LICEOF

# Copy the README from zenodo_README.md if it exists, otherwise use a minimal one.
if [ -f "$SCRIPT_DIR/zenodo_README.md" ]; then
    cp "$SCRIPT_DIR/zenodo_README.md" "$ZENODO_DIR/README.md"
else
    echo "WARNING: zenodo_README.md not found; using minimal README."
    echo "# Quantum Agrivoltaics Paper 2 — Data & Code Archive" > "$ZENODO_DIR/README.md"
    echo "See manuscript/ for details." >> "$ZENODO_DIR/README.md"
fi

# ---- Generate file manifest ----
echo "Generating file manifest..."
(cd "$ZENODO_DIR" && find . -type f | sort) > "$ZENODO_DIR/MANIFEST.txt"
FILE_COUNT=$(wc -l < "$ZENODO_DIR/MANIFEST.txt")

# ---- Create zip archive ----
ARCHIVE_NAME="quantum_agrivoltaics_paper2_zenodo_${TIMESTAMP}.zip"
echo "Creating archive: $ARCHIVE_NAME"
(cd "$SCRIPT_DIR" && zip -r "$ARCHIVE_NAME" zenodo_package/)

ARCHIVE_SIZE=$(du -sh "$SCRIPT_DIR/$ARCHIVE_NAME" | cut -f1)

echo ""
echo "=== Zenodo package build complete ==="
echo "Directory : $ZENODO_DIR"
echo "Archive   : $SCRIPT_DIR/$ARCHIVE_NAME"
echo "Files     : $FILE_COUNT"
echo "Size      : $ARCHIVE_SIZE"
echo ""
echo "Next: follow ZENODO_UPLOAD_GUIDE.md to upload."
