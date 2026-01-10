#!/bin/bash
# Auto-generate daily report for the previous day
# This script is designed to be called by launchd at midnight

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/logs/auto_report.log"
LOCK_FILE="/tmp/maclogger_daily_report.lock"

# Retry configuration
MAX_RETRIES=3
RETRY_INTERVAL=300  # 5 minutes in seconds

# Ensure log directory exists
mkdir -p "${PROJECT_ROOT}/logs"

# Log function
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Check if another instance is running (atomic operation)
if ! mkdir "${LOCK_FILE}" 2>/dev/null; then
    log_message "Another instance is already running. Exiting."
    exit 0
fi

# Ensure lock directory is removed on exit
cleanup() {
    rmdir "${LOCK_FILE}" 2>/dev/null
}
trap cleanup EXIT

# Calculate yesterday's date
YESTERDAY=$(date -v-1d +%Y-%m-%d)

log_message "=========================================="
log_message "Starting auto daily report generation for ${YESTERDAY}"

# Change to project root directory
cd "${PROJECT_ROOT}"

# Retry loop
for attempt in $(seq 1 ${MAX_RETRIES}); do
    log_message "Attempt ${attempt}/${MAX_RETRIES}..."
    
    # Run the report generator
    "${SCRIPT_DIR}/generate_report.sh" --date "${YESTERDAY}" >> "${LOG_FILE}" 2>&1
    EXIT_CODE=$?
    
    # Check result
    if [ ${EXIT_CODE} -eq 0 ]; then
        log_message "Daily report generated successfully for ${YESTERDAY} on attempt ${attempt}"
        osascript -e "display notification \"Daily report generated for ${YESTERDAY}\" with title \"MacLogger\" sound name \"Glass\"" 2>/dev/null
        log_message "Finished auto daily report generation"
        log_message "=========================================="
        exit 0
    else
        log_message "Failed to generate daily report for ${YESTERDAY} (exit code: ${EXIT_CODE})"
        
        # If not the last attempt, wait before retrying
        if [ ${attempt} -lt ${MAX_RETRIES} ]; then
            log_message "Retrying in ${RETRY_INTERVAL} seconds..."
            sleep ${RETRY_INTERVAL}
        fi
    fi
done

# All retries failed
log_message "Failed to generate daily report after ${MAX_RETRIES} attempts"
osascript -e "display notification \"Failed to generate daily report for ${YESTERDAY} after ${MAX_RETRIES} attempts\" with title \"MacLogger\" sound name \"Basso\"" 2>/dev/null
log_message "Finished auto daily report generation"
log_message "=========================================="

exit 1
