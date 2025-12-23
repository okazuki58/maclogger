#!/bin/bash
# Stop maclogger running in screen session

if ! screen -list | grep -q "maclogger"; then
    echo "maclogger is not running in a screen session."
    exit 1
fi

# Send Ctrl+C to the screen session to stop gracefully
screen -S maclogger -X stuff $'\003'

sleep 2

# Terminate the screen session
screen -S maclogger -X quit 2>/dev/null || true

echo "✓ maclogger stopped"

