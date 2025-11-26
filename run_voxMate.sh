#!/bin/bash

LOG_DIR="$HOME/voxMate/logs"
mkdir -p "$LOG_DIR"

# --- Web App (Background) ---
start_web_app() {
    if tmux has-session -t voxMate_web_app 2>/dev/null; then
        echo "Flask web app is already running."
    else
        echo "Starting web app..."
        ~/voxMate/start_voxMate_web_app.sh
    fi
}

# --- Python App (Foreground) ---
start_python_app() {
    echo "Starting Python app..."
    cd ~/voxMate/voxMate_app
    source ~/voxMate/.voxenv/bin/activate
    python3 ~/voxMate/voxMate_app/main.py
}

# --- Main ---
start_web_app
start_python_app