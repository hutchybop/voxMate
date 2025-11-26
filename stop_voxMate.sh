#!/bin/bash

# Kill the tmux session (web app)
tmux kill-session -t voxMate_web_app 2>/dev/null
echo "Stopped Flask web app (tmux session killed)"

# Kill Python app (main.py) if running
PYTHON_PID=$(pgrep -f "python3 ~/voxMate/voxMate_app/main.py")
if [ -n "$PYTHON_PID" ]; then
    kill -9 "$PYTHON_PID"
    echo "Stopped Python app (PID: $PYTHON_PID)"
else
    echo "Python app was not running"
fi

echo "voxMate app and web app stopped"