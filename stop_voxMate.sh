#!/bin/bash

# Kill the tmux session (web app)
tmux kill-session -t voxMate 2>/dev/null
echo "Stopped Flask web app (tmux session killed)"

# Kill Python app (main.py) if running
PYTHON_PID=$(pgrep -f "python3 main.py")
if [ -n "$PYTHON_PID" ]; then
    kill -9 "$PYTHON_PID"
    echo "Stopped Python app (PID: $PYTHON_PID)"
else
    echo "Python app was not running"
fi

# Unset REMOTE environment variable
unset REMOTE
echo "Removed REMOTE environment variable"

# Optional: Clear logs (uncomment if needed)
# LOG_DIR="$HOME/voxMate/logs"
# rm -f "$LOG_DIR"/*.log 2>/dev/null
# echo "Cleared log files"

echo "Cleanup complete!"