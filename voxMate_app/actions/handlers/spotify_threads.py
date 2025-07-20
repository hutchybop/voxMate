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
        try:
            playback = self.spotify_player.sp.current_playback()
            if not playback or not playback.get("is_playing"):
                logger.info("No active playback to extend")
                return

            current_track = playback.get("item")
            if not current_track:
                logger.warning("No current track info found")
                return

            # Verify authentication first
            try:
                # Simple API call to verify auth
                self.spotify_player.sp.current_user()
            except Exception as auth_error:
                logger.error(f"Authentication failed: {auth_error}")
                return

            # Try to extract artist ID (preferred)
            artist_id = current_track.get("artists", [{}])[0].get("id")
            track_id = current_track.get("id")

            # Build parameters properly
            params = {'limit': 5}
            
            if artist_id:
                params['seed_artists'] = [artist_id]
                try:
                    logger.info(f"Fetching recommendations based on artist: {artist_id}")
                    recommendations = self.spotify_player.sp.recommendations(**params)
                    if recommendations and recommendations.get('tracks'):
                        self._queue_recommendations(recommendations)
                        return
                except Exception as e:
                    logger.warning(f"Artist-based recommendation failed: {e}")

            if track_id:
                params.pop('seed_artists', None)
                params['seed_tracks'] = [track_id]
                try:
                    logger.info(f"Fetching recommendations based on track: {track_id}")
                    recommendations = self.spotify_player.sp.recommendations(**params)
                    if recommendations and recommendations.get('tracks'):
                        self._queue_recommendations(recommendations)
                        return
                except Exception as e:
                    logger.warning(f"Track-based recommendation failed: {e}")

            # Final fallback
            params.pop('seed_tracks', None)
            params['seed_genres'] = ["pop"]
            try:
                logger.info("Falling back to pop genre for recommendations")
                recommendations = self.spotify_player.sp.recommendations(**params)
                if recommendations and recommendations.get('tracks'):
                    self._queue_recommendations(recommendations)
            except Exception as e:
                logger.error(f"Genre-based fallback recommendation failed: {e}")

        except Exception as e:
            logger.error(f"Unexpected error in extend_queue: {e}")

    def _queue_recommendations(self, recommendations):
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