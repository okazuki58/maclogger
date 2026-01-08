#!/bin/bash
# Auto-generate daily report for the previous day
# This script is designed to be called by launchd at midnight

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/logs/auto_report.log"

# Ensure log directory exists
mkdir -p "${PROJECT_ROOT}/logs"

# Log function
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Calculate yesterday's date
YESTERDAY=$(date -v-1d +%Y-%m-%d)

log_message "=========================================="
log_message "Starting auto daily report generation for ${YESTERDAY}"

# Change to project root directory
cd "${PROJECT_ROOT}"

# Run the report generator
"${SCRIPT_DIR}/generate_report.sh" --date "${YESTERDAY}" >> "${LOG_FILE}" 2>&1
EXIT_CODE=$?

# Check result and send notification
if [ ${EXIT_CODE} -eq 0 ]; then
    log_message "Daily report generated successfully for ${YESTERDAY}"
    osascript -e "display notification \"Daily report generated for ${YESTERDAY}\" with title \"MacLogger\" sound name \"Glass\"" 2>/dev/null
else
    log_message "Failed to generate daily report for ${YESTERDAY} (exit code: ${EXIT_CODE})"
    osascript -e "display notification \"Failed to generate daily report for ${YESTERDAY}\" with title \"MacLogger\" sound name \"Basso\"" 2>/dev/null
fi

log_message "Finished auto daily report generation"
log_message "=========================================="

exit ${EXIT_CODE}
