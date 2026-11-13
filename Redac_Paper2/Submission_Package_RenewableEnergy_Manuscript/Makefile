# =============================================================================
# Makefile for Renewable Energy Submission Package (Elsevier)
# Target: Renewable Energy
# Date: 2026-11-12
# =============================================================================

PYTHON ?= /home/taamangtchu/miniforge3/bin/python3
CONFIG ?= parameters.yaml

.PHONY: all check test clean hpc-sync help

help:
	@echo "Available targets:"
	@echo "  make check       Validate YAML parameters consistency"
	@echo "  make test        Run local unit & analytical tests"
	@echo "  make hpc-sync    Synchronize code to HPC cluster (100.73.21.40)"
	@echo "  make clean       Remove temporary and compiled files"

check:
	@$(PYTHON) scripts/check_config.py



test: check
	@echo "Running verification suite..."
	@$(PYTHON) -m unittest discover -s tests -p "test_*.py" -v

clean:
	rm -rf *.aux *.log *.out *.bbl *.blg *.synctex.gz __pycache__ .pytest_cache
