# Required python imports
import sounddevice as sd
import time

# Required local imports
from actions.handlers.spotify_app import SpotifyPlayer
from utils.state import app_state
from utils.logging import logger


# Initisalse SportifyPlayer
spotify_player = SpotifyPlayer()

def wait_for_device_release(retries=5, delay=0.2):
    for _ in range(retries):
        try:
            sd.query_devices(kind='output')
            return True
        except Exception as e:
            logger.warning(f"Audio device not ready yet: {e}")
            time.sleep(delay)
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
            wait_for_device_release()
            app_state.set_state("spotify", "stopped")
        return stop, message

