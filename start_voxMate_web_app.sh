#!/bin/bash

# Update git to latest version
git pull

# Start the voxMate_web_app
tmux kill-session -t voxMate 2>/dev/null
tmux new-session -d -s voxMate "bash --login"
tmux send-keys -t voxMate "source ~/voxMate/.voxenv/bin/activate" C-m
tmux send-keys -t voxMate "cd ~/voxMate/voxMate_web_app" C-m
tmux send-keys -t voxMate "flask run --host=0.0.0.0 --port=5000 --debug" C-m
echo "voxMate Webapp deployed, 192.168.1.30:5000"
