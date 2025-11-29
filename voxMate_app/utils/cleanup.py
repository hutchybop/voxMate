# Required python imports
import subprocess

# Required local imports
from utils.logging import logger
from actions.handlers.spotify_app import SpotifyPlayer
from utils.mic_lights import MicLights


def cleanup() -> None:
    """Cleanup resources before exit."""
    if getattr(cleanup, "_called", False):
        return
    cleanup._called = True

    logger.info("Performing cleanup...")

    try:
        # Initialise MicLights
        lights = MicLights(num_leds=3)

        # Stop Spotify playback
        SpotifyPlayer().stop_playback()

        # Stop all mpg123 audio
        check = subprocess.run(["pgrep", "mpg123"], capture_output=True, text=True)
        if check.returncode == 0:
            # Now kill all mpg123 processes
            kill = subprocess.run(["killall", "mpg123"], capture_output=True, text=True)
            if kill.stdout:
                logger.info(f"killall output: {kill.stdout.strip()}")
            if kill.stderr:
                logger.info(f"killall errors: {kill.stderr.strip()}")

        # Turn off the mic lights
        lights.off()

    except Exception as e:
        logger.error(f"Cleanup error: {e}")
    finally:
        logger.info("Cleanup completed.")
