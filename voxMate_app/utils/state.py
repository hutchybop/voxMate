import threading
from utils.logging import logger

class AppState:
    """Thread-safe, flexible application state management"""
    
    def __init__(self):
        self._state = {
            "status": "WAITING",      # General app status
            "spotify": "stopped",     # Could be 'playing', 'paused', etc.
            "alarm": "off"            # Future: 'ringing', 'off', etc.
        }
        self._lock = threading.Lock()

    def get_state(self):
        with self._lock:
            return self._state.copy()

    def set_state(self, key, value):
        with self._lock:
            if key not in self._state:
                raise ValueError(f"Unknown state key: {key}")
            old_value = self._state[key]
            self._state[key] = value
            logger.info(f"State updated: {key} = {old_value} → {value}")

    def is_waiting(self):
        with self._lock:
            return self._state["status"] == "WAITING"

    def is_spotify_playing(self):
        with self._lock:
            return self._state["spotify"] == "playing"

# Global state instance
app_state = AppState()