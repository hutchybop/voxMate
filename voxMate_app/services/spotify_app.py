import spotipy

import config.constrants as constrants
from config.settings import load_spotify_token
from utils.logging import logger

SPOTIFY_CLIENT_ID = constrants.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = constrants.SPOTIFY_CLIENT_SECRET

def handle_spotify_play(params):
    token_info = load_spotify_token()

    if token_info is not None:
        try:
            access_token = token_info['access_token']
            sp = spotipy.Spotify(auth=access_token)
            sp.start_playback(device_id=constrants.SPOTIFY_DEVICE_ID)
        except Exception as e:
            logger.error(f"Failed to play Spotify. {e}")
    else:
        logger.error("Please login to Spotify via the web app to play Spotify.")