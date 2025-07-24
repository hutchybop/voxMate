# Required python imports
import subprocess

# Required local imports
from utils.logging import logger
from services.audio import AudioProcessor
from actions.handlers.spotify_app import SpotifyPlayer
from actions.handlers.spotify_threads import SpotifyRadioExtender
from utils.mic_lights import MicLights


def cleanup(audio_processor: AudioProcessor = None) -> None:
    """Cleanup resources before exit."""
    if getattr(cleanup, '_called', False):
        return
    cleanup._called = True

    logger.info("Performing cleanup...")

    try:
        # Initialise MicLights
        lights = MicLights(num_leds=3)

        # Stop Spotify playback
        SpotifyPlayer().stop_playback()

        # Stop radio extender thread if running
        radio_extender = SpotifyRadioExtender.get_instance()  # Assuming you're managing it as a singleton
        if radio_extender and radio_extender.is_alive():
            radio_extender.stop()
            radio_extender.join()

        # Stop looping sound if playing
        if audio_processor:
            process = getattr(audio_processor, '_current_process', None)
            audio_processor.stop_looping_sound(process=process)
        
        # Stop all mpg123 audio
        subprocess.run(["killall", "mpg123"])

        # Turn off the mic lights
        lights.off()

    except Exception as e:
        logger.error(f"Cleanup error: {e}")
    finally:
        logger.info("Cleanup completed.")