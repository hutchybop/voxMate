import threading
import time
from utils.logging import logger
from services.audio import AudioProcessor

class AudioPlaybackThread(threading.Thread):
    _instance = None

    def __init__(self, file_path: str):
        if AudioPlaybackThread._instance is not None:
            raise RuntimeError("Use start_instance() instead of creating directly.")
        super().__init__(daemon=True)
        self.file_path = file_path
        self._stop_event = threading.Event()
        AudioPlaybackThread._instance = self

    @classmethod
    def get_instance(cls):
        """Get the currently running playback thread, if any."""
        return cls._instance

    @classmethod
    def start_instance(cls, file_path: str):
        """Start a new playback thread if one is not already running."""
        if cls._instance is None:
            cls._instance = cls(file_path)
            cls._instance.start()
        else:
            logger.warning("Audio playback thread already running")
        return cls._instance

    def run(self):
        logger.info(f"Audio playback started for: {self.file_path}")
        try:
            # Non-blocking playback so the thread can stop mid-play
            AudioProcessor.play_sound(self.file_path, blocking=False)

            # Keep thread alive until stop requested or playback ends
            while not self._stop_event.is_set():
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error during audio playback: {e}")

        # Ensure audio process is stopped when thread ends
        AudioProcessor.stop_sound()

        logger.info("Audio playback thread finished")
        AudioPlaybackThread._instance = None

    def stop(self):
        logger.info("Stop requested for audio playback thread")
        self._stop_event.set()