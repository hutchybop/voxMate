# Required python imports
import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import timedelta
from flask import session, g, request
from flask_socketio import SocketIO

# Reuired local imports
from controllers.main import main
from controllers.users import users
from controllers.appSettings import appSettings
from controllers.voxSpotify import voxSpotify
from controllers.policy import policy


load_dotenv("../.env")

def create_app():

    # Setting up Flask
    app = Flask(__name__)

    # Setting up Mongo DB
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
    app.db = MongoClient(app.config["MONGODB_URI"]).get_default_database()

    # Setting up the session
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    # Setting up ioSocket
    socketio = SocketIO(app)

    # Configuring Flask app settings
    app.config["SESSION_COOKIE_NAME"] = "voxMate_session"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = True if os.environ.get("FLASK_ENV") == "production" else False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_REFRESH_EACH_REQUEST"] = True
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=48)
    app.config["WTF_CSRF_ENABLED"] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    REQUIRED_ENV_VARS = ['GROQ_API_KEY', 'PORCUPINE_API_KEY', 'MONGODB_URI', 'SECRET_KEY']


    @app.before_request
    def check_env_variables():

        # Skip static files and assets
        if request.endpoint in ('static', None) or not request.accept_mimetypes.accept_html:
            return

        g.missing_env_vars = None

        if session.get('env_checked'):
            return

        missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing:
            g.missing_env_vars = missing


    @app.route('/dismiss-env-warning', methods=['POST'])
    def dismiss_env_warning():
        session['env_checked'] = True
        return '', 204  # No Content
    
    # Using the imported routes
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(appSettings)
    app.register_blueprint(voxSpotify)
    app.register_blueprint(policy)

    # Making socketio avaiable in appSettings
    appSettings.socketio = socketio

    return app
