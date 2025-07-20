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
            logger.warning("No current track info found")
            return

        # Try to extract artist ID (preferred)
        artist_id = current_track.get("artists", [{}])[0].get("id")
        track_id = current_track.get("id")

        recommendations = None

        # Try with artist ID
        if artist_id:
            try:
                logger.info(f"Fetching recommendations based on artist: {artist_id}")
                recommendations = self.spotify_player.sp.recommendations(seed_artists=artist_id, limit=5)
            except Exception as e:
                logger.warning(f"Artist-based recommendation failed: {e}")

        # Fallback to track ID
        if (not recommendations or not recommendations.get("tracks")) and track_id:
            try:
                logger.info(f"Fetching recommendations based on track: {track_id}")
                recommendations = self.spotify_player.sp.recommendations(seed_tracks=track_id, limit=5)
            except Exception as e:
                logger.warning(f"Track-based recommendation failed: {e}")

        # Final fallback to genre
        if not recommendations or not recommendations.get("tracks"):
            try:
                logger.info("Falling back to pop genre for recommendations")
                recommendations = self.spotify_player.sp.recommendations(seed_genres="pop", limit=5)
            except Exception as e:
                logger.error(f"Genre-based fallback recommendation failed: {e}")
                return

        # Queue the recommended tracks
        for track in recommendations.get("tracks", []):
            uri = track.get("uri")
            name = track.get("name")
            artist_name = track.get("artists", [{}])[0].get("name")
            if uri:
                try:
                    self.spotify_player.sp.add_to_queue(uri)
                    logger.info(f"Queued recommendation: {name} by {artist_name}")
                except Exception as e:
                    logger.warning(f"Failed to queue track {name}: {e}")


    def stop(self):
        logger.info("Stopping Spotify radio extender thread")
        self._running = False