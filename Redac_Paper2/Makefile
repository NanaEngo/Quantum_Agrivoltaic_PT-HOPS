.PHONY: lint format check clean test

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix --unsafe-fixes src/ tests/

check:
	ruff check src/ tests/
	ruff format --check src/ tests/

test:
	python -m pytest tests/unit/ -v --tb=short

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
