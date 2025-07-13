# Required local import
from utils.logging import logger
from services.audio import AudioProcessor
from services.spotify_app import SpotifyPlayer

def cleanup() -> None:
    """Cleanup resources before exit"""
    if hasattr(cleanup, '_called'):
        return
    cleanup._called = True  # Mark as called to prevent duplicate execution
    logger.info("Performing cleanup...")
    try:
        # Stop Spotify if playing
        spotify = SpotifyPlayer()
        spotify.stop_playback()
        # Stop looping sound if playing
        audio = AudioProcessor()
        audio.stop_looping_sound()
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
    finally:
        logger.info("Cleanup completed")