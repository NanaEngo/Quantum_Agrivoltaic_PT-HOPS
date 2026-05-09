"""
conftest.py — Shared pytest fixtures and logging setup for all test modules.

All test files import `test_logger` from here; results are written to
reproducibility/logs/tests_<YYYYMMDD>.log alongside the simulation logs.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

import pytest

# ── Log file location (same directory as simulation logs) ─────────────────────
_LOG_DIR = Path(__file__).parent.parent / "reproducibility" / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / f"tests_{datetime.now().strftime('%Y%m%d')}.log"

_FMT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
_formatter = logging.Formatter(_FMT, datefmt="%H:%M:%S")

# File handler (append so multiple pytest runs accumulate in one daily file)
_fh = logging.FileHandler(_LOG_FILE, mode="a")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(_formatter)

# Console handler — use stderr so pytest doesn't suppress it
_ch = logging.StreamHandler(sys.stderr)
_ch.setLevel(logging.INFO)
_ch.setFormatter(_formatter)

# Root test logger
_root = logging.getLogger("tests")
if not _root.handlers:          # avoid duplicate handlers on re-import
    _root.setLevel(logging.DEBUG)
    _root.addHandler(_fh)
    _root.addHandler(_ch)


def get_test_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'tests' hierarchy."""
    return logging.getLogger(f"tests.{name}")


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def session_log_banner():
    """Log a session-start banner once per pytest run."""
    _root.info("=" * 60)
    _root.info(f"TEST SESSION START — {datetime.now().isoformat()}")
    _root.info(f"Log file: {_LOG_FILE}")
    _root.info("=" * 60)
    yield
    _root.info("=" * 60)
    _root.info(f"TEST SESSION END   — {datetime.now().isoformat()}")
    _root.info("=" * 60)


@pytest.fixture(autouse=True)
def log_test_outcome(request):
    """Log PASSED / FAILED / SKIPPED for every test automatically."""
    logger = get_test_logger(request.node.nodeid)
    logger.info(f"START  {request.node.nodeid}")
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep is None:
        outcome = "UNKNOWN"
    elif rep.passed:
        outcome = "PASSED"
    elif rep.failed:
        outcome = "FAILED"
    else:
        outcome = "SKIPPED"
    logger.info(f"{outcome} {request.node.nodeid}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach the call report to the item so log_test_outcome can read it."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        item.rep_call = rep
