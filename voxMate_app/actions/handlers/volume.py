# Reuired python imports
import subprocess
from typing import Optional, Tuple

# Required local imports
from utils.state import app_state
from utils.logging import logger


def change_volume(level) -> Tuple[bool, Optional[str]]:
    """
    Changes the system and Spotify volume levels:
    - "up": increases volume by 10 (max 100)
    - "down": decreases volume by 10 (min 0)
    - "max": sets volume to 100
    - "min": sets volume to 0
    - Otherwise tries to interpret level as a number between 0 and 100
    """
    try:
        # Get the current system volume
        current_volume = int(app_state.get_state("volume"))
        # Handle string input
        if isinstance(level, str):
            # Standadising the level string
            level = level.lower().strip()
            if level.endswith("%"):
                level = level[:-1]
            # Handling commands
            if level == "up":
                new_volume = min(100, current_volume + 10)
            elif level == "down":
                new_volume = max(0, current_volume - 10)
            elif level == "min":
                new_volume = 0
            elif level == "max":
                new_volume = 100
            else:
                # Trys to convert string number to int
                try:
                    new_volume = max(0, min(100, int(level)))
                except ValueError:
                    logger.error(f"Invalid volume level string: '{level}'")
                    return False, "Invalid volume level"
        else:
            # Non-string input; try converting to int directly
            try:
                new_volume = max(0, min(100, int(level)))
            except ValueError:
                logger.error(f"Invalid volume level input: {level}")
                return False, "Invalid volume level"
        # Set system volume
        subprocess.run(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{new_volume}%"], check=True
        )
        app_state.set_state("volume", new_volume)
        logger.info(f"Volume now set to: {new_volume}")
        return True, None
    except Exception as e:
        logger.error(f"Error changing system volume: {e}")
        return False, "Error trying to set new volume"
