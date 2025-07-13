# Required python imports
import threading

# Required local imports
from utils.logging import logger

# Improved state tracking with thread safety
class AppState:
    """Thread-safe application state management"""
    _states = {
        "WAITING": "Waiting for wake word",
        "WAITING_SPOTIFY": "Waiting for wake word, while playing Spotify",
        "PROCESSING": "Processing response"
    }

    def __init__(self):
        self._state = "WAITING"
        self._lock = threading.Lock()

    @property
    def state(self):
        with self._lock:
            return self._state

    def set_state(self, new_state):
        with self._lock:
            if new_state in self._states:
                old_state = self._state
                self._state = new_state
                logger.debug(f"State changed: {old_state} → {new_state}")
            else:
                raise ValueError(f"Invalid state: {new_state}")
            
    def is_waiting(self):
        if self.state in ["WAITING", "WAITING_SPOTIFY"]:
            return True

# Global state instance
app_state = AppState()