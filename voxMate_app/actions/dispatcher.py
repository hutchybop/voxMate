# Required python imports
from typing import Optional, Tuple

# Required local imports
from actions.handlers.spotify_app import SpotifyPlayer
from actions.handlers.volume import change_volume
from utils.state import app_state
from utils.logging import logger


# Initisalse
spotify_player = SpotifyPlayer()


def handle_action(parsed) -> Tuple[bool, Optional[str]]:
    logger.info("=== ACTION DISPATCHER START ===")
    logger.debug(f"Received parsed action: {parsed}")

    message = ""
    action = parsed.get("action", "")
    logger.info(f"Dispatching action: {action}")

    if action == "spotify_play":
        logger.info("Handling spotify_play action")
        # Extracting params
        query = parsed.get("query", "")
        artist = parsed.get("artist", "")
        type = parsed.get("type", "")
        params = {"query": query, "artist": artist, "type": type}
        logger.debug(f"Spotify play params: {params}")

        # Send params to handle_spotify_play
        success, message = spotify_player.handle_spotify_play(params)
        logger.info(f"Spotify play result - Success: {success}, Message: {message}")

        if success:
            logger.info("Updating app state to spotify:playing")
            app_state.set_state("spotify", "playing")
        elif not message:
            message = "Error playing Spotify"
            logger.warning("No error message provided, using default")
        return success, message

    elif action == "spotify_stop":
        logger.info("Handling spotify_stop action")
        success, message = spotify_player.stop_playback()
        logger.info(f"Spotify stop result - Success: {success}, Message: {message}")

        if success:
            logger.info("Updating app state to spotify:stopped")
            app_state.set_state("spotify", "stopped")
        elif not message:
            message = "Error stopping Spotify"
            logger.warning("No error message provided, using default")
        return success, message

    elif action == "spotify_skip":
        logger.info("Handling spotify_skip action")
        success, message = spotify_player.skip_playback()
        logger.info(f"Spotify skip result - Success: {success}, Message: {message}")

        if not success and not message:
            message = "Error skipping Spotify"
            logger.warning("No error message provided, using default")
        return success, message

    elif action == "spotify_repeat":
        repeat = parsed.get("repeat", "").lower().strip()
        logger.info(f"Handling spotify_repeat action with repeat mode: {repeat}")
        success, message = spotify_player.repeat_playback(repeat)
        logger.info(f"Spotify repeat result - Success: {success}, Message: {message}")

        if not success and not message:
            message = "Error toggling repeat mode"
            logger.warning("No error message provided, using default")
        return success, message

    elif action == "spotify_shuffle":
        shuffle = {"true": True, "false": False}.get(
            parsed.get("shuffle", "").lower().strip()
        )
        logger.info(f"Handling spotify_shuffle action with shuffle mode: {shuffle}")
        success, message = spotify_player.shuffle_playback(shuffle)
        logger.info(f"Spotify shuffle result - Success: {success}, Message: {message}")

        if success:
            logger.info("Updating app state to spotify:playing")
            app_state.set_state("spotify", "playing")
        elif not message:
            message = "Error toggling shuffle mode"
            logger.warning("No error message provided, using default")
        return success, message

    elif action == "volume":
        level = parsed.get("level", "")
        logger.info(f"Handling volume action with level: {level}")
        if not level:
            logger.error("No volume level provided")
            return False, "No volume level provided"
        success, message = change_volume(level)
        logger.info(f"Volume change result - Success: {success}, Message: {message}")

        if not success and not message:
            message = "Error setting volume"
            logger.warning("No error message provided, using default")
        return success, message

    elif action == "news":
        logger.info("Handling news action")
        params = {"query": "news"}
        success, message = spotify_player.handle_spotify_play(params)
        logger.info(f"News playback result - Success: {success}, Message: {message}")

        if not success and not message:
            message = "Error getting the news"
            logger.warning("No error message provided, using default")
        return success, message

    else:
        logger.warning(f"Unknown action received: {action}")
        return False, f"Unknown action: {action}"
