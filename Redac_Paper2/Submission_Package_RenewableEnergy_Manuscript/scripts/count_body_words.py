#!/usr/bin/env python3
"""
Count body words in the manuscript, as required by the journal length gate.

Two numbers are printed:

* ``prose``   -- the main text with tables, figures, equations, nomenclature and the
                bibliography removed, and with inline/display math, citation and
                cross-reference macros stripped;
* ``with captions`` -- the same count plus the words in table and figure captions.

The method is deliberately mechanical so that the number quoted at submission can be
regenerated: substitute a different `grep -c` or a word processor and the total will
move by a few per cent, which is why the counting rule is stated in the checklist.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STRIP_ENVS = ("table", "figure", "equation", "align", "tabular", "array")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")


def _strip_math_and_macros(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\(cite[a-z]*|cref|Cref|ref|label|eqref)\{[^}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", text)
    return re.sub(r"[{}~]", " ", text)


def body(tex: str) -> str:
    return tex.split(r"\begin{document}")[1].split(r"\bibliographystyle")[0]


def prose_words(tex: str) -> int:
    text = body(tex)
    for env in STRIP_ENVS:
        text = re.sub(
            r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (env, env), " ", text, flags=re.S
        )
    return len(WORD_RE.findall(_strip_math_and_macros(text)))


def caption_words(tex: str) -> int:
    text = body(tex)
    captions = re.findall(r"\\caption\{(.*?)\}\s*\\label", text, flags=re.S)
    captions += re.findall(r"\\caption\[.*?\]\{(.*?)\}\s*\\label", text, flags=re.S)
    return sum(len(WORD_RE.findall(_strip_math_and_macros(c))) for c in captions)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tex", default=str(BASE_DIR / "RE_main_2611.tex"))
    args = parser.parse_args()
    tex = Path(args.tex).read_text(encoding="utf-8")
    prose = prose_words(tex)
    caps = caption_words(tex)
    print(f"prose: {prose}")
    print(f"with captions: {prose + caps}")


if __name__ == "__main__":
    main()
