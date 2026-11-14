# =============================================================================
# Makefile for Renewable Energy Submission Package (Elsevier)
# Target: Renewable Energy
# Date: 2026-11-13
# =============================================================================

PYTHON ?= python3
CONFIG ?= parameters.yaml

.PHONY: all check test clean help

help:
	@echo "Available targets:"
	@echo "  make check       Validate YAML parameters consistency"
	@echo "  make test        Run package verification tests (pytest)"
	@echo "  make clean       Remove temporary and compiled files"

check:
	@$(PYTHON) scripts/check_config.py



test: check
	@echo "Running verification suite..."
	@$(PYTHON) -m pytest tests -q

clean:
	rm -rf *.aux *.log *.out *.bbl *.blg *.synctex.gz __pycache__ .pytest_cache
