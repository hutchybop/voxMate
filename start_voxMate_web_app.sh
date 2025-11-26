#!/bin/bash

# Start the voxMate_web_app
tmux kill-session -t voxMate_web_app 2>/dev/null
tmux new-session -d -s voxMate_web_app "bash --login"
tmux send-keys -t voxMate_web_app "source ~/voxMate/.voxenv/bin/activate" C-m
tmux send-keys -t voxMate_web_app "cd ~/voxMate/voxMate_web_app" C-m
tmux send-keys -t voxMate_web_app "export FLASK_DEBUG=1" C-m
tmux send-keys -t voxMate_web_app "flask run --host=0.0.0.0 --port=5000 --debug" C-m
echo "voxMate Webapp deployed, 192.168.1.30:5000"
