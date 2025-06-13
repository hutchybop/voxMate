import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

from controllers.routes import pages

load_dotenv("../.env")

def create_app():

    # Setting up Flask
    app = Flask(__name__)

    # Setting up Mongo DB
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
    app.db = MongoClient(app.config["MONGODB_URI"]).get_default_database()

    # Setting up the session
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    
    # Using the imported routes from pages
    app.register_blueprint(pages)

    return app