# Required python imports

# Required local imports
from actions.handlers.spotify_app import SpotifyPlayer
from utils.state import app_state


# Initisalse
spotify_player = SpotifyPlayer()
radio_extender = None  # Global thread reference


def handle_cmd(action):
    global radio_extender
    message = ""
    command = action.get('cmd', '')
    params = action.get('params', '')

    if command == 'spotify_play':
        success, message = spotify_player.handle_spotify_play(params)
        if success:
            app_state.set_state("spotify", "playing")
        else:
            if not message:
                message = "Error playing Spotify"
        return success, message

    elif command == 'spotify_stop':
        success = spotify_player.stop_playback()
        if success:
            app_state.set_state("spotify", "stopped")
        else:
            message = "Error stopping Spotify"
        return success, message

