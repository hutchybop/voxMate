# Required python imports

# Required local imports
from actions.handlers.spotify_app import SpotifyPlayer
from utils.state import app_state
from actions.handlers.spotify_threads import SpotifyRadioExtender


# Initisalse
spotify_player = SpotifyPlayer()
radio_extender = None  # Global thread reference


def handle_cmd(cmd):
    global radio_extender
    message = ""
    command = cmd.get('cmd')

    if command == 'spotify_play':
        play, message = spotify_player.handle_spotify_play(cmd)
        if play:
            app_state.set_state("spotify", "playing")
            if not radio_extender or not radio_extender.is_alive():
                radio_extender = SpotifyRadioExtender(spotify_player, app_state)
                radio_extender.start()
        else:
            if not message:
                message = "Error playing Spotify"
        return play, message

    elif command == 'spotify_stop':
        stop = spotify_player.stop_playback()
        if stop:
            app_state.set_state("spotify", "stopped")
            if radio_extender and radio_extender.is_alive():
                radio_extender.stop()
                radio_extender.join()
        else:
            message = "Error stopping Spotify"
        return stop, message

