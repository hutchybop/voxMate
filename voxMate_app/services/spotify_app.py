import spotipy

import config.constrants as constrants
from config.settings import load_spotify_token
from utils.logging import logger

SPOTIFY_CLIENT_ID = constrants.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = constrants.SPOTIFY_CLIENT_SECRET

def handle_spotify_play(params):
    token_info = load_spotify_token()

    if token_info is not None:
        print("SPOTIFY: 'token_info is not None'")
        access_token = token_info['access_token']
        try:
            
            sp = spotipy.Spotify(auth=access_token)

            devices = sp.devices()
            print("SPOTIFY: Available Devices:", devices)

            response_transfer = sp.transfer_playback(device_id='b16c033229c6e42b50fcc84989e90f4fc0be26c0', force_play=True)
            print("SPOTIFY: Transfer Playback response:", response_transfer)

            import time; time.sleep(3)

            response = sp.start_playback(device_id='b16c033229c6e42b50fcc84989e90f4fc0be26c0', uris=["spotify:track:3n3Ppam7vgaVa1iaRUc9Lp"])
            print("SPOTIFY: Playback response:", response)

        except Exception as e:
            print("SPOTIFY: Playback error: ", e)
            import traceback
            traceback.print_exc()
    else:
        logger.error("Please login to Spotify via the web app to play Spotify.")