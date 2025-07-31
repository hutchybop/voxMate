# Required python imports
from typing import Optional, Tuple

# Required local imports
from actions.handlers.spotify_app import SpotifyPlayer
from utils.state import app_state


# Initisalse
spotify_player = SpotifyPlayer()


def handle_action(parsed) -> Tuple[bool, Optional[str]]:
    message = ""
    action = parsed.get("action", "")

    if action == 'spotify_play':
        # Extracting params
        query = parsed.get("query", "")
        artist = parsed.get("artist", "")
        type = parsed.get("type", "")
        params = {"query": query, "artist": artist, "type": type}
        # Send params to handle_spotify_play
        success, message = spotify_player.handle_spotify_play(params)
        if success:
            app_state.set_state("spotify", "playing")
        elif not message:
            message = "Error playing Spotify"
        return success, message

    elif action == 'spotify_stop':
        success, message = spotify_player.stop_playback()
        if success:
            app_state.set_state("spotify", "stopped")
        elif not message:
            message = "Error playing Spotify"
        return success, message
    
    elif action == 'spotify_skip':
        success, message = spotify_player.skip_playback()
        if not success and not message:
            message = "Error skipping Spotify"
        return success, message
    
    elif action == 'spotify_repeat':
        repeat = parsed.get("repeat", "").lower().strip()
        success, message = spotify_player.repeat_playback(repeat)
        if not success and not message:
            message = "Error toggling repeat mode"
        return success, message
    
    elif action == 'spotify_shuffle':
        shuffle = {"true": True, "false": False}.get(parsed.get("shuffle", "").lower().strip())
        success, message = spotify_player.shuffle_playback(shuffle)
        if not success and not message:
            message = "Error toggling shuffle mode"
        return success, message
