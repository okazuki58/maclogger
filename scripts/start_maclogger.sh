#!/bin/bash
# Start maclogger in a screen session

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"
source venv/bin/activate

# Check if already running
if screen -list | grep -q "maclogger"; then
    echo "maclogger is already running in a screen session."
    echo "To attach: screen -r maclogger"
    exit 1
fi

# Start in detached screen session
screen -S maclogger -d -m python src/maclogger.py

echo "✓ maclogger started in screen session"
echo ""
echo "Useful commands:"
echo "  Attach:  screen -r maclogger"
echo "  Detach:  Ctrl+A, D"
echo "  Stop:    make stop"
echo "  Status:  make status"


