# Required python imports
import threading
import time

# Required local imports
from utils.logging import logger


class SpotifyRadioExtender(threading.Thread):
    def __init__(self, spotify_player, app_state, interval=30):
        super().__init__(daemon=True)
        self.spotify_player = spotify_player
        self.app_state = app_state
        self.interval = interval  # Time between queue updates
        self._running = True

    def run(self):
        logger.info("Spotify radio extender thread started")
        while self._running:
            if self.app_state.is_spotify_playing():
                try:
                    self.extend_queue()
                except Exception as e:
                    logger.error(f"Error in queue extender: {e}")
            time.sleep(self.interval)

    def extend_queue(self):
        playback = self.spotify_player.sp.current_playback()
        if not playback or not playback.get("is_playing"):
            return

        current_track = playback.get("item")
        if not current_track:
            return

        seed_id = current_track.get("id")
        if not seed_id:
            return

        logger.info(f"Fetching recommendations based on track: {seed_id}")
        recommendations = self.spotify_player.sp.recommendations(seed_tracks=[seed_id], limit=3)
        for track in recommendations.get("tracks", []):
            uri = track.get("uri")
            if uri:
                self.spotify_player.sp.add_to_queue(uri)
                logger.info(f"Queued recommendation: {track.get('name')} by {track.get('artists')[0]['name']}")

    def stop(self):
        logger.info("Stopping Spotify radio extender thread")
        self._running = False