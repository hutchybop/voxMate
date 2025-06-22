import os
import secrets
import time
from flask import Flask, redirect, request, session, url_for, render_template_string
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import urlencode

# Load environment variables
load_dotenv('../../.env')

# Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
SCOPES = 'user-read-currently-playing user-modify-playback-state user-read-playback-state'

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Disable spotipy's default file cache
os.environ['SPOTIPY_CACHE'] = ''

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_handler=None
    )

user_tokens = {}

def is_token_expired(token_info):
    return time.time() > token_info['expires_at']

def refresh_token_if_needed(user_id):
    token_info = user_tokens.get(user_id)
    if not token_info:
        return None
    
    if is_token_expired(token_info):
        oauth = create_spotify_oauth()
        new_token_info = oauth.refresh_access_token(token_info['refresh_token'])
        
        if not new_token_info:
            return None
        
        token_info.update(new_token_info)
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        user_tokens[user_id] = token_info
    
    return token_info

@app.route('/')
def index():
    if 'user_id' not in session:
        # Force show_dialog=True when logging in again after logout
        auth_url = create_spotify_oauth().get_authorize_url()
        return f"""
            <h1>Spotify Login</h1>
            <a href="{auth_url}">Login with Spotify</a>
        """
    
    user_id = session['user_id']
    token_info = refresh_token_if_needed(user_id)
    
    if not token_info:
        return redirect('/logout')
    
    try:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        current_user = sp.current_user()
        return f"""
            <h1>Welcome {current_user['display_name']}!</h1>
            <p>You are logged in with Spotify.</p>
            <a href="/logout">Logout</a>
        """
    except Exception as e:
        return redirect(f'/error?message={str(e)}')

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return redirect(f'/error?message={request.args["error"]}')
    
    code = request.args.get('code')
    if not code:
        return redirect('/error?message=No authorization code received')

    try:
        oauth = create_spotify_oauth()
        token_info = oauth.get_access_token(code)
        
        if not token_info:
            return redirect('/error?message=Failed to get access token')
        
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        
        user_id = secrets.token_urlsafe(16)
        session['user_id'] = user_id
        user_tokens[user_id] = token_info
        
        return redirect('/')
    except Exception as e:
        return redirect(f'/error?message={str(e)}')

@app.route('/logout')
def logout():
    # 1. Clear Flask session
    if 'user_id' in session:
        user_id = session.pop('user_id')
        user_tokens.pop(user_id, None)  # Safely remove if exists

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Logout Complete</title>
        <style>
            .logout-box {
                max-width: 500px;
                margin: 2rem auto;
                padding: 2rem;
                text-align: center;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            .btn {
                display: inline-block;
                padding: 10px 20px;
                background: #1DB954;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <div class="logout-box">
            <h2>You've been logged out</h2>
            <p>For complete security, please also log out from Spotify:</p>

            <!-- User-triggered logout button -->
            <button class="btn" onclick="logoutFromSpotify()">Log Out from Spotify</button>

            <p>
                <a href="/">Return to homepage</a>
            </p>
        </div>

        <script>
        function logoutFromSpotify() {
            // Open Spotify logout page in a new tab
            window.open('https://accounts.spotify.com/en/logout', '_blank', 'noopener,noreferrer');

            // Redirect current tab to home
            window.location.href = '/';
        }
        </script>
    </body>
    </html>
    """


@app.route('/error')
def error():
    error_message = request.args.get('message', 'An unknown error occurred')
    return f"""
        <h1>Error</h1>
        <p>{error_message}</p>
        <a href="/">Try again</a>
    """

if __name__ == '__main__':
    app.run(debug=True)