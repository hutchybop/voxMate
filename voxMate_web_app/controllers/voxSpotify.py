import os
import time
import spotipy
import uuid
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, render_template, current_app, session, redirect, url_for, flash, request
from dotenv import load_dotenv
from models.decorators import isLoggedIn

voxSpotify = Blueprint(
    "voxSpotify", __name__, template_folder="templates", static_folder="static"
)

load_dotenv("../../.env")

# Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_CALLBACK_URI')
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
    user_id = session["user_id"]
    token_info = None
    user_token = current_app.db.voxSpotify.find_one({'user_id': user_id})

    if user_token:
        token_info = user_token.get("token_info")
        if time.time() > token_info['expires_at']:
            oauth = create_spotify_oauth()
            new_token_info = oauth.refresh_access_token(token_info['refresh_token'])
            if not new_token_info:
                return None
            else:
                current_app.db.voxSpotify.update_one({'user_id': user_id}, {'$set': {'token_info': new_token_info}})
                return new_token_info
                
    return token_info


@voxSpotify.route("/voxSpotify")
@isLoggedIn
def voxSpotify_index():

    print(f"DEBUG: URI: ", REDIRECT_URI)

    # Get the user token from the db and refresh if required
    token_info = get_token_and_refresh()

    # Show spotify login page if no toke_info
    if not token_info:
        state = str(uuid.uuid4())
        session['spotify_auth_state'] = state
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



@voxSpotify.route('/voxSpotify/callback')
@isLoggedIn
def callback():

    # Sends user to the error page if there is either 'error' or no 'code' in callback url
    if 'error' in request.args:
        flash(f"There has been an error: {request.args['error']} \n Please try again.", "danger")
        return redirect(url_for('voxSpotify.voxSpotify_index'))
    code = request.args.get('code')
    if not code:
        flash(f"Login error, no authorisation code received. \n Please try again.", "danger")
        return redirect(url_for('voxSpotify.voxSpotify_index'))
    
    # Checks for CSRF attack
    returned_state = request.args.get('state')
    expected_state = session.pop('spotify_auth_state', None)
    if not returned_state or returned_state != expected_state:
        flash("Invalid state parameter. Please try logging in again.", "danger")
        return redirect(url_for('voxSpotify.voxSpotify_index'))

    try:
        # Creates the user's spotify token and saves it in the db
        oauth = create_spotify_oauth()
        token_info = oauth.get_access_token(code)
        
        # More error handling
        if not token_info:
            flash("Error getting login token. \n Please try again.", "danger")
            return redirect(url_for('voxSpotify.voxSpotify_index'))
        
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        
        # Store token_info in MongoDB
        current_app.db.voxSpotify.insert_one({
            'user_id': session["user_id"],
            'token_info': token_info
        })


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