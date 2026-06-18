#!/usr/bin/env bash
#===============================================================================
# run_tests.sh — Launch Paper 2 test suite inside the MesoHOP-sim conda env
#
# Usage:
#   ./run_tests.sh                          # Run all unit tests
#   ./run_tests.sh -v                       # Verbose mode
#   ./run_tests.sh -k mesohops              # Run only MesoHOPS-related tests
#   ./run_tests.sh --coverage               # Run with coverage report
#===============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="MesoHOP-sim"

echo "========================================================================"
echo "  Quantum Agrivoltaics — Paper 2 Test Suite"
echo "  Environment: ${ENV_NAME}"
echo "  Directory:   ${SCRIPT_DIR}"
echo "========================================================================"
echo ""

# Detect conda
if ! command -v conda &>/dev/null; then
    echo "ERROR: 'conda' command not found. Are you in a Miniforge/Miniconda installation?"
    exit 1
fi

# Check that the target environment exists
if ! conda env list | grep -q "${ENV_NAME}"; then
    echo "ERROR: Conda environment '${ENV_NAME}' not found."
    echo "       Create it with: conda create -n ${ENV_NAME} python=3.12 mesohops h5py pyyaml pydantic"
    exit 1
fi

# Build pytest arguments
PYTEST_ARGS=()
VERBOSE=false
COVERAGE=false

for arg in "$@"; do
    case "$arg" in
        --coverage)
            COVERAGE=true
            ;;
        *)
            PYTEST_ARGS+=("$arg")
            ;;
    esac
done

if [ ${#PYTEST_ARGS[@]} -eq 0 ]; then
    PYTEST_ARGS+=("-v")
fi

echo "Running: PYTHONPATH=${SCRIPT_DIR} conda run -n ${ENV_NAME} pytest tests/unit/ ${PYTEST_ARGS[*]}"
echo ""

if [ "$COVERAGE" = true ]; then
    conda run -n "${ENV_NAME}" \
        python -m pytest "${PYTEST_ARGS[@]}" \
        --cov="${SCRIPT_DIR}/src" \
        --cov-report=term \
        --cov-report=html:"${SCRIPT_DIR}/coverage_html" \
        "${SCRIPT_DIR}/tests/unit/"
else
    conda run -n "${ENV_NAME}" \
        python -m pytest "${PYTEST_ARGS[@]}" \
        "${SCRIPT_DIR}/tests/unit/"
fi

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed."
else
    echo "❌ Some tests failed (exit code: ${EXIT_CODE})."
fi

exit $EXIT_CODE
