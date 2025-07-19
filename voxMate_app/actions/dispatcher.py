# Required python imports
import sounddevice as sd
import time

# Required local imports
from actions.handlers.spotify_app import SpotifyPlayer
from utils.state import app_state
from utils.logging import logger


# Initisalse SportifyPlayer
spotify_player = SpotifyPlayer()

def wait_for_device_release(retries=10, delay=0.1):
    for i in range(retries):
        try:
            # Try to initialize a dummy stream to force device release
            with sd.OutputStream(samplerate=44100, channels=1, dtype='float32'):
                pass
            return True
        except Exception as e:
            logger.warning(f"Audio device not ready (attempt {i+1}/{retries}): {e}")
            time.sleep(delay)
    logger.error("Failed to release audio device after multiple attempts")
    return False

def handle_cmd(cmd):
    """Handles user commands"""
    # Setting up message
    message = ""

    # Play stoptify
    if cmd.get('cmd') == 'spotify_play':
        play = spotify_player.handle_spotify_play(cmd)
        if not play:
            message = "Error playing Spotify"
        else:
            app_state.set_state("spotify", "playing")
        return play, message

    # Stop stoptify
    if cmd.get('cmd') == 'spotify_stop':
        stop = spotify_player.stop_playback()
        if not stop:
            message = "Error stopping Spotify"
        else:
            # wait_for_device_release()
            app_state.set_state("spotify", "stopped")
        return stop, message

