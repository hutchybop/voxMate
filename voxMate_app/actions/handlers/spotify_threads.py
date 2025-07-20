# Required python imports
import threading
import time

# Required local imports
from utils.logging import logger


class SpotifyRadioExtender(threading.Thread):
    _instance = None  # Singleton instance

    def __init__(self, spotify_player, app_state, interval=30):
        if SpotifyRadioExtender._instance is not None:
            raise RuntimeError("Use get_instance() to access the SpotifyRadioExtender singleton.")
        super().__init__(daemon=True)
        self.spotify_player = spotify_player
        self.app_state = app_state
        self.interval = interval
        self._stop_event = threading.Event()
        SpotifyRadioExtender._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance

    @classmethod
    def start_instance(cls, spotify_player, app_state, interval=30):
        if cls._instance is None:
            cls._instance = cls(spotify_player, app_state, interval)
            cls._instance.start()
        return cls._instance


    def run(self):
        logger.info("Spotify radio extender thread started")
        while not self._stop_event.is_set():
            if self.app_state.is_spotify_playing():
                try:
                    self.extend_queue()
                except Exception as e:
                    logger.error(f"Error in queue extender: {e}")
            # Wait for up to `interval` seconds, but return immediately if stop is set
            self._stop_event.wait(timeout=self.interval)


    def extend_queue(self):
        # Check and refresh the users Spotify access token
        self.spotify_player.load_spotify_token()
        
        playback = self.spotify_player.sp.current_playback()
        if not playback or not playback.get("is_playing"):
            return

        current_track = playback.get("item")
        current_uri = current_track.get("uri") if current_track else None

        try:
            # Try to get current queue (Spotify API now supports this)
            queue_info = self.spotify_player.sp.queue()
            queued_uris = [t["uri"] for t in queue_info.get("queue", [])]
        except Exception as e:
            logger.warning(f"Could not fetch queue info: {e}")
            queued_uris = []

        artist_id = current_track.get("artists", [{}])[0].get("id") if current_track else None
        if not artist_id:
            logger.warning("No artist ID found")
            return

        try:
            logger.info(f"Fetching top tracks for artist: {artist_id}")
            top_tracks = self.spotify_player.sp.artist_top_tracks(artist_id, country="GB")["tracks"]

            added = 0
            for track in top_tracks:
                uri = track["uri"]
                if uri == current_uri or uri in queued_uris or uri in getattr(self, "_queued_uris", set()):
                    continue  # Skip if currently playing or already queued/added

                self.spotify_player.sp.add_to_queue(uri)
                logger.info(f"Queued new top track: {track['name']} by {track['artists'][0]['name']}")
                self._queued_uris = getattr(self, "_queued_uris", set())
                self._queued_uris.add(uri)

                added += 1
                if added >= 3:
                    break  # Limit how many we add at a time

        except Exception as e:
            logger.error(f"Failed to fetch or queue top tracks: {e}")


    def stop(self):
        logger.info("Stopping Spotify radio extender thread")
        self._stop_event.set()
        SpotifyRadioExtender._instance = None