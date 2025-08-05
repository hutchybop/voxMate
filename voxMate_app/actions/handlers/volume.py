# Reuired python imports
import subprocess
from typing import Optional, Tuple

# Required local imports
from utils.state import app_state
from utils.logging import logger


def change_volume(level) -> Tuple[bool, Optional[str]]:
    """
    Changes the system and Spotify volume levels:
    - up: +10
    - down: -10
    - max: 100
    - min: 0
    - Sets volume to user defined level
    """
    try:
        # Sanitising level and removing % sign if present
        if level is str:
            level = level.lower().strip()
            if level.endswith('%'):
                level = level[:-1]
            # Getting the current volume from app_state
            current_volume = int(app_state.get_state("volume"))
            # Defining new_volume based on input level
            if level == "up":
                new_volume = min(100, current_volume + 10)
            elif level == "down":
                new_volume = max(0, current_volume - 10)
            elif level == "min":
                new_volume = 0
            elif level == "max":
                new_volume = 100
        else:
            # Trying to convert input to an integer and clamp to 0–100
            try:
                new_volume = max(0, min(100, int(level)))
            except ValueError as e:
                logger.error(f"Error converting volume level to int: {e}")
                return False, "Error trying to set new volume"
        # Setting the new system volume using pactl
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{new_volume}%"], check=True)
        # Storing the new volume in app_state
        app_state.set_state("volume", new_volume)
        logger.info(f"Volume now set to: {new_volume}")
        return True, None
    except Exception as e:
        logger.error(f"Error changing system volume: {e}")
        return False, "Error trying to set new volume"


