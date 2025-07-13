# Required local import
from utils.logging import logger
from services.audio import AudioProcessor
from services.spotify_app import SpotifyPlayer

def cleanup(audio_processor=None) -> None:
    """Cleanup resources before exit"""
    if hasattr(cleanup, '_called'):
        return
    cleanup._called = True  # Mark as called to prevent duplicate execution
    logger.info("Performing cleanup...")
    try:
        # Stop Spotify if playing
        SpotifyPlayer().stop_playback()
        # Stop looping sound if playing
        if audio_processor:
            audio_processor.stop_looping_sound(process=getattr(audio_processor, '_current_process', None))
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
    finally:
        logger.info("Cleanup completed")