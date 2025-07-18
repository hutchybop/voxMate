from actions.handlers.spotify_app import SpotifyPlayer
from utils.state import app_state

# Initisalse SportifyPlayer
spotify_player = SpotifyPlayer()

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
            app_state.set_state("spotify", "stopped")
        return stop, message

