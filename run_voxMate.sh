#!/bin/bash

LOG_DIR="$HOME/voxMate/logs"
mkdir -p "$LOG_DIR"

# --- Remote Mode Prompt ---
read -p "Are you working remotely? (y/n): " is_remote
if [[ "$is_remote" =~ ^[yY] ]]; then
    export REMOTE="True"
    echo "Remote mode enabled"
else
    export REMOTE="False"
    echo "Local mode"
fi

# --- Web App (Background) ---
start_web_app() {
    if pgrep -f "flask run" >/dev/null; then
        echo "Flask web app is already running."
    else
        echo "Starting web app (logs: $LOG_DIR/webapp.log)..."
        cd ~/voxMate/voxMate_web_app
        source ~/voxMate/.voxenv/bin/activate
        export FLASK_DEBUG=1
        nohup flask run --host=0.0.0.0 --port=5000 --debug > "$LOG_DIR/webapp.log" 2>&1 &
        echo "Web app running: http://192.168.1.30:5000"
    fi
}

# --- Python App (Foreground) ---
start_python_app() {
    echo "Starting Python app..."
    cd ~/voxMate/voxMate_app
    source ~/voxMate/.voxenv/bin/activate
    # Redirect stderr to suppress ONNX Runtime GPU warnings
    python3 main.py 2> >(grep -v "GPU device discovery failed" >&2)
    # python3 main.py
}

# --- Git Update ---
update_git() {
    echo "Updating git repository..."
    git -C ~/voxMate pull
}

# --- Main ---
update_git
start_web_app
start_python_app  # Now has access to $REMOTE