# Required python imports
import threading

# Required local imports
from typing import Optional, Dict, Union
from utils.logging import logger


class AppState:
    """Thread-safe, flexible application state management"""

    def __init__(self) -> None:
        self._state = {
            "status": "waiting",  # General app status
            "spotify": "stopped",  # Could be 'playing', 'paused', etc.
            "volume": 70,  # Current voulme setting
            "alarm": "off",  # Future: 'ringing', 'off', etc.
        }
        self._lock = threading.Lock()

    def get_state(
        self, key: Optional[str] = None
    ) -> Union[Dict[str, Union[str, int]], Optional[Union[str, int]]]:
        if key:
            with self._lock:
                return self._state.get(key)
        with self._lock:
            return self._state.copy()

    def set_state(self, key: str, value: Union[str, int]) -> None:
        with self._lock:
            if key not in self._state:
                raise ValueError(f"Unknown state key: {key}")
            old_value = self._state[key]
            self._state[key] = value
            logger.info(f"State updated: {key} = {old_value} → {value}")

    def is_waiting(self) -> bool:
        with self._lock:
            return self._state["status"] == "waiting"

    def is_spotify_playing(self) -> bool:
        with self._lock:
            return self._state["spotify"] == "playing"

    def is_spotify_paused(self) -> bool:
        with self._lock:
            return self._state["spotify"] == "paused"


# Global state instance
app_state = AppState()
