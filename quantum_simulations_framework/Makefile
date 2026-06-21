.PHONY: lint format check clean

lint:
	ruff check src/ reproducibility/

format:
	ruff format src/ reproducibility/
	ruff check --fix --unsafe-fixes src/ reproducibility/

check:
	ruff check src/ reproducibility/
	ruff format --check src/ reproducibility/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
