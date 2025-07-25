#!/usr/bin/env python3

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env vars
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add parent directories to path to import modules
sys.path.append(str(Path(__file__).resolve().parent))

# Now import necessary modules
from actions.dispatcher import handle_cmd
from utils.logging import logger

def test_handle_spotify():
    # Simulate an AI response's action
    action = {
        "cmd": "spotify_play",
        "artist": "Radiohead",
        "track": "Paranoid Android",
        "type": "track"
    }

    success, message = handle_cmd(action)
    logger.info(f"Success: {success}")
    logger.info(f"Message: {message}")

if __name__ == "__main__":
    test_handle_spotify()