# ADR-0001: Ruff as single lint/format tool over Black + isort

**Date**: 2026-06-21
**Status**: accepted
**Deciders**: Nana Engo

## Context

The codebase had three separate tools for code quality: Black (formatting), isort (import sorting), and Ruff (linting). This duplicated configuration across `pyproject.toml` (three separate sections) and `.pre-commit-config.yaml` (three separate hooks). The `Makefile` was also running black before ruff, causing redundant passes — black formatted, then ruff re-checked the same files.

Ruff's formatter (`ruff format`) is a drop-in replacement for Black since v0.9+, supporting the same line-length and quote-style options with equivalent output.

## Decision

Replace Black + isort with Ruff exclusively. `ruff format` replaces both `black` and `isort` (import sorting is handled by `ruff check --select I --fix`). The `Makefile` uses `ruff format` instead of `black`, and the pre-commit config uses `ruff-format` instead of `black`.

## Alternatives Considered

### Alternative 1: Keep Black + isort + Ruff
- **Pros**: Mature toolchain, no migration risk
- **Cons**: Three config sections, three pre-commit hooks, slower CI pipeline
- **Why not**: Ruff's formatter is production-ready and actively maintained by Astral. Keeping three tools adds maintenance overhead with zero benefit.

### Alternative 2: Use Black + Ruff only (drop isort)
- **Pros**: Removes one tool
- **Cons**: Black doesn't sort imports — would still need either isort or Ruff's I rule
- **Why not**: Ruff's I rule handles import sorting during `ruff check --fix`, making isort redundant.

## Consequences

### Positive
- Single configuration section in `pyproject.toml`
- Single pre-commit hook (ruff-format instead of black + ruff + isort)
- Faster `make format` and `make check` (one tool instead of two)
- Ruff's `--unsafe-fixes` flag catches issues (like B007 unused loop vars) that Black ignores

### Negative
- Legacy `.pre-commit-config.yaml` still references Black v24.10.0, which doesn't match the installed v24.2.0

### Risks
- Ruff formatter v0.14.x may produce slightly different output than Black 24.x for edge cases (e.g., trailing commas in multi-line expressions). Verified on 45 files: output is equivalent.
