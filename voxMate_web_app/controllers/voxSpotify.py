import os
import time
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, render_template, current_app, session, redirect, url_for, flash, request, jsonify
from dotenv import load_dotenv
from models.decorators import isLoggedIn
from utils.api import contact_api_server
from models.models import VoxMate
from dataclasses import asdict


voxSpotify = Blueprint(
    "voxSpotify", __name__, template_folder="templates", static_folder="static"
)

load_dotenv("../../.env")

# Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'https://voxmate.longrunner.co.uk/voxSpotify/callback'
SCOPES = " ".join([
    "user-read-currently-playing",
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-library-read",
    "playlist-read-private"
])

# Disable spotipy's default file cache
os.environ['SPOTIPY_CACHE'] = ''

# Setup spotipy's auth
def create_spotify_oauth(state=None):
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_handler=None,
        state=state
    )

def get_token_and_refresh():
    token_info = None
    user_token = current_app.db.voxSpotify.find_one({'user_id': session.get("user_id")})

    if user_token:
        token_info = user_token.get("token_info")
        if time.time() > token_info['expires_at']:
            oauth = create_spotify_oauth()
            new_token_info = oauth.refresh_access_token(token_info['refresh_token'])
            if not new_token_info:
                return None
            else:
                current_app.db.voxSpotify.update_one({'user_id': session.get("user_id")}, {'$set': {'token_info': new_token_info}})
                return new_token_info
                
    return token_info


@voxSpotify.route("/voxSpotify")
@isLoggedIn
def voxSpotify_index():

    # Get the user token from the db and refresh if required
    token_info = get_token_and_refresh()

    # Show spotify login page if no toke_info
    if not token_info:
        user = current_app.db.users.find_one({"user_id": session.get("user_id")})
        state = user.get("api_token")
        auth_url = create_spotify_oauth(state=state).get_authorize_url()
        return render_template('voxSpotify/voxSpotify_index.html', title="voxMate - Spotify Login", auth_url=auth_url)
    
    try:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        current_user = sp.current_user()
        return render_template('voxSpotify/voxSpotify_profile.html', title="voxMate - Spotify Profile", current_user=current_user)
    
    except Exception as e:
        # Delete token from DB to force re-auth on next load
        current_app.db.voxSpotify.delete_one({"user_id": session['user_id']})
        flash(f"There has been an error: {str(e)} \n Please log in again.", "danger")
        return redirect(url_for('voxSpotify.voxSpotify_index'))



@voxSpotify.route('/voxSpotify/waiting')
@isLoggedIn
def waiting():
    if request.args.get('waiting') == "true":
        return render_template('voxSpotify/voxSpotify_waiting.html', title="voxMate - Spotify Waiting")
    else:
        flash("Please login to Spotify first", "warning")
        return redirect(url_for("voxSpotify.voxSpotify.index"))


@voxSpotify.route('/voxSpotify/check_status')
@isLoggedIn
def check_status():
    user = current_app.db.users.find_one({"user_id": session.get("user_id")})
    if not user:
        return jsonify({"status": "user"})
    
    state = user.get("api_token")
    payload = {"user_id": session.get("user_id"), "state": state}
    response, error = contact_api_server(payload, "voxSpotify/waiting")
    if response:
        if response.get("user_code"):
            user_code = response.get("user_code")
            # Add it to the voxspotify collection
            user = current_app.db.voxSpotify.find_one({session.get("user_id")})
            # If the user is already in the db update, if not add new user
            if user:
                current_app.db.voxSpotify.update_one({session.get("user_id")}, {"$Set": {"user_code": user_code}})
            else:
                user_spotify = VoxMate(
                    user_id=session.get("user_id"),
                    user_code=user_code
                )
                current_app.db.voxSpotify.insert_one(asdict(user_spotify))
            return jsonify({"status": "user_code"})
        if response.get("user"):
            return jsonify({"status": "user"})
        if response.get("vox"):
            return jsonify({"status": "vox"})
        if response.get("error"):
            return jsonify({"status": "spotify_error", "error": error})
    elif error:
        return jsonify({"status": "server_error", "error": error})

    return jsonify({"status": "pending"})



@voxSpotify.route('/voxSpotify/callback')
@isLoggedIn
def callback():

    voxSpotify = current_app.db.voxSpotify.find_one({"user_id": session.get("user_id")})
    if not voxSpotify:
        flash("No Spotify login details save. Please try again")
        return redirect(url_for("voxSpotify.voxSpotify_index"))
    
    user_code = voxSpotify.get('user_code')
    if not user_code:
        flash(f"Login error, no authorisation code received. \n Please try again.", "danger")
        return redirect(url_for('voxSpotify.voxSpotify_index'))

    try:
        # Creates the user's spotify token and saves it in the db
        oauth = create_spotify_oauth()
        token_info = oauth.get_access_token(user_code)
        
        # More error handling
        if not token_info:
            flash("Error getting login token. \n Please try again.", "danger")
            return redirect(url_for('voxSpotify.voxSpotify_index'))
        
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        
        # Store token_info in MongoDB
        current_app.db.voxSpotify.update_one(
            {'user_id': session.get("user_id")},
            {"$set": {'token_info': token_info, "user_code": None}}
        )

        return redirect(url_for('voxSpotify.voxSpotify_index'))
    
    except Exception as e:
        flash(f"There has been an error: {str(e)} \n Please try again.", "danger")
        return redirect(url_for('voxSpotify.voxSpotify_index'))

@voxSpotify.route('/voxSpotify/logout')
@isLoggedIn
def voxSpotify_logout():
    token_info = get_token_and_refresh()
    if token_info:
        current_app.db.voxSpotify.delete_one({"user_id": session['user_id']})
    
    return render_template('voxSpotify/voxSpotify_logout.html', title="voxMate - Spotify Logout")