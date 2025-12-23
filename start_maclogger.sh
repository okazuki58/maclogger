#!/bin/bash
# Start maclogger in a screen session

cd /Users/ogawakazuki/dev/maclogger
source venv/bin/activate

# Check if already running
if screen -list | grep -q "maclogger"; then
    echo "maclogger is already running in a screen session."
    echo "To attach: screen -r maclogger"
    exit 1
fi

# Start in detached screen session
screen -S maclogger -d -m python maclogger.py

echo "✓ maclogger started in screen session"
echo ""
echo "Useful commands:"
echo "  Attach:  screen -r maclogger"
echo "  Detach:  Ctrl+A, D"
echo "  Stop:    ./stop_maclogger.sh"
echo "  Status:  screen -ls | grep maclogger"

