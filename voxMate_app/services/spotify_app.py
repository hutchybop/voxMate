import spotipy
import time
import requests

import config.constrants as constrants
from config.settings import load_spotify_token
from config.settings import load_user
from utils.logging import logger

SPOTIFY_CLIENT_ID = constrants.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = constrants.SPOTIFY_CLIENT_SECRET

def handle_spotify_play(params):

        token_info = load_spotify_token()
        # print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: token_info = ", token_info)

        if not token_info:
            logger.error("Please login to Spotify via the web app to play Spotify.")
            return

        sp = spotipy.Spotify(auth=token_info['access_token'])

        # Find raspotify device
        devices = sp.devices().get('devices', [])
        print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: devices-1: ", devices)
        raspotify = next((d for d in devices if 'voxMate' in d['name']), None)
        print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: raspotify-1: ", raspotify)
        if not raspotify:
            print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: No active raspotify device found. Trying to wake it up...")

            # Dummy playback to activate device
            try:
                sp.start_playback(uris=["spotify:track:7GhIk7Il098yCjg4BQjzvb"])  # Rickroll
                time.sleep(1)
                sp.pause_playback()
                time.sleep(1)
            except Exception as e:
                print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: Wake-up playback failed:", e)

            # Refresh devices
            devices = sp.devices().get('devices', [])
            print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: devices-2: ", devices)
            raspotify = next((d for d in devices if 'voxMate' in d['name']), None)
            print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: raspotify-2: ", raspotify)

        if not raspotify:
            print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: Still no device found.")
            return

        device_id = raspotify['id']
        print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: device_id: ", device_id)

        sp.transfer_playback(device_id=device_id, force_play=True)
        time.sleep(1)
        sp.start_playback(device_id=device_id)

    # token_info = load_spotify_token()
    # print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: token_info = ", token_info)

    # if token_info is not None:

    #     print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: 'token_info is not None'")
    #     access_token = token_info['access_token']
    #     try:
            
    #         sp = spotipy.Spotify(auth=access_token)

    #         devices = sp.devices()
    #         print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: Available Device: ", devices)

    #         response_transfer = sp.transfer_playback(device_id='b16c033229c6e42b50fcc84989e90f4fc0be26c0', force_play=True)
    #         print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: Transfer Playback respons: ", response_transfer)

    #         time.sleep(3)

    #         # response = sp.start_playback(device_id='b16c033229c6e42b50fcc84989e90f4fc0be26c0', uris=["spotify:track:3n3Ppam7vgaVa1iaRUc9Lp"])
    #         response = sp.start_playback(device_id='b16c033229c6e42b50fcc84989e90f4fc0be26c0')
    #         print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: Playback response:", response)

    #     except Exception as e:
    #         print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: Playback error: ", e)
    #         import traceback
    #         traceback.print_exc()
    # else:
    #     logger.error("Please login to Spotify via the web app to play Spotify.")

    # try:
    #     user = load_user()
    #     user_id = user.get("user_id")

    #     payload = { "user_id": user_id}
    #     response = requests.get("http://localhost:5000/voxSpotify/playback", json=payload)

    #     if response.status_code == 200:
    #         data = response.json()
    #         success = data.get("success")
    #         message = data.get("message")
    #         if success:
    #             print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: Playback triggered")
    #         elif message:
    #             print("APP.services.spotify_app.py.handle_spotifyvoxMate_app: ", message)
    #     else:
    #         print("Error:", response.status_code, response.text)
    # except Exception as e:
    #     logger.error(f"Error trying to play Spotify: {e}")