#!/bin/bash
# Generate daily report from hourly summaries

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_PYTHON="${PROJECT_ROOT}/venv/bin/python"
REPORT_SCRIPT="${PROJECT_ROOT}/src/generate_report.py"

# Check if venv exists
if [ ! -f "${VENV_PYTHON}" ]; then
    echo "Error: Python virtual environment not found."
    echo "Please run: make setup"
    exit 1
fi

# Change to project root directory to ensure relative paths work
cd "${PROJECT_ROOT}"

# Run the report generator with all arguments passed through
"${VENV_PYTHON}" "${REPORT_SCRIPT}" "$@"


