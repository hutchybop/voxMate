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

        artist_id = current_track.get("artists", [{}])[0].get("id")
        if not artist_id:
            logger.warning("No artist ID found")
            return

        try:
            logger.info(f"Fetching top tracks for artist: {artist_id}")
            top_tracks = self.spotify_player.sp.artist_top_tracks(artist_id, country="GB")["tracks"]
            for track in top_tracks[:3]:
                self.spotify_player.sp.add_to_queue(track["uri"])
                logger.info(f"Queued top track: {track['name']} by {track['artists'][0]['name']}")
        except Exception as e:
            logger.error(f"Failed to fetch or queue top tracks: {e}")

    def stop(self):
        logger.info("Stopping Spotify radio extender thread")
        self._running = False