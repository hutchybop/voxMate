import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import timedelta

from controllers.main import main
from controllers.users import users
from controllers.appSettings import appSettings


load_dotenv("../.env")

def create_app():

    # Setting up Flask
    app = Flask(__name__)

    # Setting up Mongo DB
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
    app.db = MongoClient(app.config["MONGODB_URI"]).get_default_database()

    # Setting up the session
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

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
    
    # Using the imported routes
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(appSettings)

    return app