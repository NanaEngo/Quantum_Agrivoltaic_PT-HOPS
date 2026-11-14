#!/usr/bin/env python3
"""
Emit a SHA-256 manifest of the submission package (mitigation item M11, local part).

Hashes every file that determines a reported number or a compiled page: manuscript and
supporting-material sources, the parameter file, scripts, tests, figure sources and the
primary data artifacts. Build products, caches and PDFs are excluded, because they are
reproducible from the hashed inputs and would otherwise change on every compile.

Usage:
    python3 scripts/make_release_manifest.py [--out docs/CHECKSUMS_SHA256.txt]
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INCLUDE_SUFFIXES = {".tex", ".bib", ".yaml", ".yml", ".py", ".csv", ".json", ".npz", ".md"}
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "figures", "docs/research-agrivoltaic-opv-coffee-tea-penja-pepper"}
EXCLUDE_NAMES = {"CHECKSUMS_SHA256.txt"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect() -> list[Path]:
    files: list[Path] = []
    for path in sorted(BASE_DIR.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(BASE_DIR)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_NAMES:
            continue
        if path.suffix.lower() not in INCLUDE_SUFFIXES:
            continue
        files.append(path)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="docs/CHECKSUMS_SHA256.txt")
    args = parser.parse_args()

    files = collect()
    lines = [f"{_sha256(p)}  {p.relative_to(BASE_DIR).as_posix()}" for p in files]
    dest = BASE_DIR / args.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {dest} ({len(lines)} files)")


if __name__ == "__main__":
    main()
