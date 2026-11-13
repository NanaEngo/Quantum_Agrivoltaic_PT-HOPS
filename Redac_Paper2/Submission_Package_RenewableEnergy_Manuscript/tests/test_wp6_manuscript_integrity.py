#!/usr/bin/env python3
"""Integrity tests for WP6 figures, Data Analysis Report, and Renewable Energy LaTeX submission package."""

import re
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FIGURE_BASENAMES = [
    "Fig1_Optical_Pareto_Spectral_TMM",
    "Fig2_Quantum_NESS_Bound_Benchmark",
    "Fig3_Microclimate_Cooling_Dry_Wet_Regimes",
    "Fig4_Four_Lever_Causal_Attribution_Phase",
    "Fig5_Dispatch_TEA_LCA_BreakEven",
    "Fig6_Sobol_Uncertainty_LER_Policy",
]

MANUSCRIPT_BASENAMES = [
    "RE_main_2611",
    "RE_SM_2611",
    "RE_Highlights_2611",
    "RE_Cover_letter_2611",
]


class TestWP6ManuscriptIntegrity(unittest.TestCase):
    def test_figures_and_artifacts_exist_and_nonempty(self) -> None:
        """All 6 PDF + 600 DPI PNG figures, Data Analysis Report, and BibTeX database exist."""
        fig_dir = BASE_DIR / "figures"
        for stem in FIGURE_BASENAMES:
            pdf = fig_dir / f"{stem}.pdf"
            png = fig_dir / f"{stem}.png"
            self.assertTrue(pdf.exists(), f"Missing vector PDF figure: {pdf}")
            self.assertTrue(png.exists(), f"Missing 600 DPI PNG figure: {png}")
            self.assertGreater(pdf.stat().st_size, 10_000, f"Empty/corrupt PDF: {pdf}")
            self.assertGreater(png.stat().st_size, 100_000, f"Low-res/empty PNG: {png}")

        for stem in MANUSCRIPT_BASENAMES:
            tex = BASE_DIR / f"{stem}.tex"
            pdf = BASE_DIR / f"{stem}.pdf"
            self.assertTrue(tex.exists(), f"Missing LaTeX source: {tex}")
            self.assertTrue(pdf.exists(), f"Missing compiled PDF: {pdf}")
            self.assertGreater(pdf.stat().st_size, 10_000, f"Empty compiled PDF: {pdf}")

        report = BASE_DIR / "docs" / "DATA_ANALYSIS_REPORT_20261113.md"
        self.assertTrue(report.exists(), "Missing WP6 Data Analysis Report")
        self.assertGreater(report.stat().st_size, 5_000)

        bib = BASE_DIR / "references.bib"
        self.assertTrue(bib.exists(), "Missing references.bib")
        self.assertGreater(bib.stat().st_size, 10_000)

    def test_required_latex_packages_and_geometry(self) -> None:
        """RE_main_2611 and RE_SM_2611 enforce siunitx, cleveref, xr[nocite], and margin=2cm."""
        for stem, ext_target in [("RE_main_2611", "RE_SM_2611"), ("RE_SM_2611", "RE_main_2611")]:
            tex = (BASE_DIR / f"{stem}.tex").read_text(encoding="utf-8")
            self.assertIn(r"\usepackage[margin=2cm]{geometry}", tex)
            self.assertIn(r"\usepackage{siunitx}", tex)
            self.assertIn(r"\usepackage{xr}", tex)
            self.assertRegex(tex, r"\\usepackage\[[^\]]*\]\{cleveref\}")
            self.assertIn(f"[nocite]{{{ext_target}}}", tex)
            # No accidental Markdown emphasis markers or text-mode \mathrm inside \texttt
            self.assertNotRegex(tex, r"\*[A-Za-z]")
            self.assertNotRegex(tex, r"\\texttt\{[^$}]*\\mathrm")

        highlights = (BASE_DIR / "RE_Highlights_2611.tex").read_text(encoding="utf-8")
        self.assertIn(r"\usepackage[margin=2cm]{geometry}", highlights)
        cover = (BASE_DIR / "RE_Cover_letter_2611.tex").read_text(encoding="utf-8")
        self.assertIn(r"\usepackage[margin=2cm]{geometry}", cover)

    def test_elsevier_highlights_character_limit(self) -> None:
        """Elsevier Highlights bullets stay strictly <= 85 rendered characters each."""
        highlights_tex = (BASE_DIR / "RE_Highlights_2611.tex").read_text(encoding="utf-8")
        bullets = re.findall(r"\\item\s+(.+)", highlights_tex)
        self.assertGreaterEqual(len(bullets), 3)
        self.assertLessEqual(len(bullets), 5)
        for idx, bullet in enumerate(bullets, start=1):
            no_comment = re.sub(r"\s*(?<!\\)%.*$", "", bullet).strip()
            rendered = (
                no_comment.replace(r"\%", "%")
                .replace(r"\$", "$")
                .replace("--", "-")
                .replace("$", "")
                .replace(r"\mathrm{", "")
                .replace(r"\Delta\eta_{\mathrm{NESS}}", "dEta_NESS")
                .replace(r"\le", "<=")
                .replace(r"\ge", ">=")
                .replace(r"\times", "x")
                .replace(r"\,^\circ", "deg")
            )
            self.assertLessEqual(len(rendered), 85, f"Highlight #{idx} exceeds 85 chars ({len(rendered)}): {rendered}")

    def test_citations_and_xr_labels_resolve(self) -> None:
        """Every \\cite{...} resolves in references.bib and every sm:... \\cref resolves in RE_SM_2611."""
        bib_text = (BASE_DIR / "references.bib").read_text(encoding="utf-8")
        bib_keys = set(re.findall(r"@\w+\{([^,\s]+),", bib_text))
        sm_tex = (BASE_DIR / "RE_SM_2611.tex").read_text(encoding="utf-8")
        main_tex = (BASE_DIR / "RE_main_2611.tex").read_text(encoding="utf-8")
        sm_labels = set(re.findall(r"\\label\{([^}]+)\}", sm_tex))

        for tex_name, tex_src in [("RE_main_2611.tex", main_tex), ("RE_SM_2611.tex", sm_tex)]:
            for cite_group in re.findall(r"\\cite\{([^}]+)\}", tex_src):
                for key in cite_group.split(","):
                    k = key.strip()
                    self.assertIn(k, bib_keys, f"Citation key '{k}' in {tex_name} missing from references.bib")

        for sm_ref in re.findall(r"\\(?:c?ref)\{sm:([^}]+)\}", main_tex):
            self.assertIn(sm_ref, sm_labels, f"Cross-reference 'sm:{sm_ref}' missing from RE_SM_2611.tex")

        # Require >= 50 unique cited references in RE_main_2611.tex per journal maturity standard
        main_cites = {k.strip() for g in re.findall(r"\\cite\{([^}]+)\}", main_tex) for k in g.split(",")}
        self.assertGreaterEqual(len(main_cites), 50, f"Expected >=50 cited references, got {len(main_cites)}")

    def test_elsevier_author_guideline_compliance(self) -> None:
        """Enforce Renewable Energy author guidelines: corresponding author, abstract<=250w, zero keyword overlap, declarations."""
        main_tex = (BASE_DIR / "RE_main_2611.tex").read_text(encoding="utf-8")
        sm_tex = (BASE_DIR / "RE_SM_2611.tex").read_text(encoding="utf-8")
        cover_tex = (BASE_DIR / "RE_Cover_letter_2611.tex").read_text(encoding="utf-8")

        self.assertIn("Serge Guy Nana Engo\\corref{cor1}", main_tex)
        self.assertIn("Serge Guy Nana Engo\\corref{cor1}", sm_tex)
        self.assertIn("serge.nana-engo@facsciences-uy1.cm", cover_tex)
        self.assertIn(r"\usepackage{lineno}", main_tex)
        self.assertIn(r"\linenumbers", main_tex)
        self.assertIn(r"\section*{Nomenclature}", main_tex)
        self.assertIn(r"\section*{CRediT authorship contribution statement}", main_tex)
        self.assertIn(r"\section*{Declaration of competing interest}", main_tex)
        self.assertIn(r"\section*{Declaration of generative AI", main_tex)
        self.assertIn(r"\section*{Data availability}", main_tex)

        m_abs = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main_tex, re.S)
        self.assertIsNotNone(m_abs)
        abs_plain = re.sub(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{[^}]*\})*", " ", m_abs.group(1))
        abs_words = re.findall(r"[A-Za-z0-9\-\+%$]+", abs_plain)
        self.assertLessEqual(len(abs_words), 250, f"Abstract too long ({len(abs_words)} words > 250)")

        title_words = {
            w for w in re.findall(r"[a-z]+", re.search(r"\\title\{(.*?)\}", main_tex, re.S).group(1).lower())
            if len(w) > 3
        }
        kw_words = {
            w for w in re.findall(r"[a-z]+", re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", main_tex, re.S).group(1).lower())
            if len(w) > 3
        }
        self.assertEqual(sorted(title_words & kw_words), [], "Keywords repeat Title words")

        # Require Interpretive framework subsection and forbid overclaiming "theorem" wording
        self.assertIn(r"\label{sec:interpretive}", main_tex)
        self.assertNotIn("decoupling theorem", main_tex.lower())
        # Ensure zero Markdown inline-code backticks (`...`) leaked into LaTeX
        for tex_name, tex_src in [("RE_main_2611.tex", main_tex), ("RE_SM_2611.tex", sm_tex), ("RE_Cover_letter_2611.tex", cover_tex)]:
            without_latex_open_quotes = tex_src.replace("``", "")
            self.assertNotIn("`", without_latex_open_quotes, f"Markdown backtick leaked into {tex_name}")

        # Elsevier Copyediting rule & anti-report-style hygiene:
        # 1) Zero bullet/numbered lists in main body prose (continuous IMRAD paragraphs only)
        self.assertNotIn(r"\begin{itemize}", main_tex, "Bullet list found in RE_main_2611.tex")
        self.assertNotIn(r"\begin{enumerate}", main_tex, "Numbered list found in RE_main_2611.tex")
        self.assertNotIn(r"\begin{enumerate}", cover_tex, "Numbered list found in RE_Cover_letter_2611.tex")

        # 2) Zero internal file names, script paths, YAML versions, ledger labels, or raw snake_case tokens
        forbidden_report_tokens = [
            "parameters.yaml",
            "v2.5.0",
            "wp5b_sobol_robustness",
            "verification ledger",
            "= inf",
            "(inf)",
            r"\texttt{s3\_opv",
            r"\texttt{s2\_csi",
            r"\texttt{s5\_opv",
            r"\texttt{no\_bess",
            r"\texttt{overnight\_withering",
            r"\texttt{offgrid\_no\_export",
            r"\texttt{vpd\_p95",
            r"\texttt{t80\_",
            r"\texttt{mesohops",
        ]
        for tex_name, tex_src in [("RE_main_2611.tex", main_tex), ("RE_SM_2611.tex", sm_tex), ("RE_Cover_letter_2611.tex", cover_tex)]:
            low = tex_src.lower()
            for tok in forbidden_report_tokens:
                self.assertNotIn(tok, low, f"Report-style token '{tok}' found in {tex_name}")

        # 3) No \textbf emphasis inside running body prose (permitted only in table headers and CRediT author names)
        for lineno, line in enumerate(main_tex.splitlines(), start=1):
            if r"\textbf{" not in line:
                continue
            is_table_header = "&" in line and r"\\" in line
            is_credit_line = "Conceptualization" in line and "Serge Guy Nana Engo" in line
            self.assertTrue(
                is_table_header or is_credit_line,
                f"Disallowed inline prose \\textbf on RE_main_2611.tex:{lineno}: {line.strip()[:80]}",
            )

    def test_compiled_logs_clean_when_present(self) -> None:
        """If TeX compile logs exist locally, confirm zero fatal errors or unresolved refs."""
        for stem in MANUSCRIPT_BASENAMES:
            log_path = BASE_DIR / f"{stem}.log"
            if not log_path.exists():
                continue
            log_txt = log_path.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn("! LaTeX Error:", log_txt, f"LaTeX error found in {log_path.name}")
            self.assertNotIn("! Undefined control sequence.", log_txt, f"Undefined control sequence in {log_path.name}")
            self.assertNotIn("There were undefined references.", log_txt, f"Undefined ref in {log_path.name}")
            self.assertNotIn("There were undefined citations.", log_txt, f"Undefined cite in {log_path.name}")
            self.assertNotIn("multiply defined", log_txt, f"Multiply defined label/cite in {log_path.name}")


if __name__ == "__main__":
    unittest.main()
