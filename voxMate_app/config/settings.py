# Required python imports
import os
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.database import Database
from spotipy.oauth2 import SpotifyOAuth

# Required local imports
from services.audio import AudioProcessor
from utils.logging import logger
import config.constrants as constrants


# ================= CONFIGURATION =================
# Constants for default values
DEFAULT_CONFIG = {
    "SILENCE_THRESHOLD": 14200,
    "SILENCE_DURATION": 1.0,
    "VOLUME_DISPLAY": False,
    "NOISE_REDUCTION_ENABLED": True,
    "STT_MODEL": "whisper-large-v3-turbo",
    "AI_MODEL": "mistral-saba-24b"
}

def load_user() -> Optional[Dict[str, Any]]:
    # Load user config if exists
    config_path = Path(__file__).resolve().parent.parent.parent / "userConfig" / "user_config.json"
    user_config = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            user_config = json.load(f)
            # print("APP.config.settings.load_user: user_config: ", user_config)
            return user_config
    else:
        logger.error("Please login to play spotify and customise settings")
        return None

def load_mongodb() -> Optional[Database]:
    # Try to connect to MongoDB if URI is available
    mongodb_uri = os.getenv("MONGODB_URI")
    if mongodb_uri:
        try:
            mongodb = MongoClient(mongodb_uri).get_default_database()
            return mongodb
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return None
        

def load_config() -> Dict[str, Any]:
    """Load configuration from user file and MongoDB with fallbacks."""
    # Finds the user if they have logged in
    user_config = load_user()
    mongodb = load_mongodb()

    if mongodb is not None:
        try:            
            # Try user settings first, then fall back to default settings
            settings = mongodb.appSettings.find_one({"user_id": user_config.get("user_id")}) or {}

            if not settings:
                settings = mongodb.appSettings.find_one({"user_id": "default"}) or {}

            logger.info("User config settings loaded")

            # Build final config with proper fallback order
            return {
                "SILENCE_THRESHOLD": settings.get('silence_threshold', DEFAULT_CONFIG["SILENCE_THRESHOLD"]),
                "SILENCE_DURATION": settings.get('silence_duration', DEFAULT_CONFIG["SILENCE_DURATION"]),
                "VOLUME_DISPLAY": settings.get('volume_display', DEFAULT_CONFIG["VOLUME_DISPLAY"]),
                "NOISE_REDUCTION_ENABLED": settings.get('noise_reduction', DEFAULT_CONFIG["NOISE_REDUCTION_ENABLED"]),
                "STT_MODEL": settings.get('stt_model', DEFAULT_CONFIG["STT_MODEL"]),
                "AI_MODEL": settings.get('ai_model', DEFAULT_CONFIG["AI_MODEL"]),
            }
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            

    # Fallback to defaults if MongoDB not available
    logger.warning("Using default configuration")
    return DEFAULT_CONFIG


# Setup spotipy's auth
def create_spotify_oauth(state=None):
    return SpotifyOAuth(
        client_id=constrants.SPOTIFY_CLIENT_ID,
        client_secret=constrants.SPOTIFY_CLIENT_SECRET,
        redirect_uri=constrants.REDIRECT_URI,
        scope=constrants.SCOPES,
        cache_handler=None,
        state=state
    )


def load_spotify_token():
    user_config = load_user()
    mongodb = load_mongodb()

    # print("APP.config.settings.load_spotify_token: user_config: ", user_config)
    # print("APP.config.settings.load_spotify_token: mongodb: ", mongodb)

    if user_config is None:
        return None
    
    if mongodb is not None:
        try:
            # print("APP.config.settings.load_spotify_token: 'mongodb is not None'")
            user_id = user_config.get("user_id")
            # print("APP.config.settings.load_spotify_token: user_id: ", user_id)
            token_info = None
            user_token = mongodb.voxSpotify.find_one({'user_id': user_id})
            # print("APP.config.settings.load_spotify_token: user_token (db_call): ", user_token)

            if user_token:
                token_info = user_token.get("token_info")
                # print("APP.config.settings.load_spotify_token: token_info: ", token_info)
                if time.time() > token_info['expires_at']:
                    oauth = create_spotify_oauth()
                    new_token_info = oauth.refresh_access_token(token_info['refresh_token'])
                    # print("APP.config.settings.load_spotify_token: new_token_info: ", new_token_info)
                    if not new_token_info:
                        return None
                    else:
                        mongodb.voxSpotify.update_one({'user_id': user_id}, {'$set': {'token_info': new_token_info}})
                        return new_token_info
                        
            return token_info
        except:
            return None


# Load configuration when module is imported
CONFIG = load_config()


# Make settings available as module-level constants
SILENCE_THRESHOLD = CONFIG["SILENCE_THRESHOLD"]
SILENCE_DURATION = CONFIG["SILENCE_DURATION"]
VOLUME_DISPLAY = CONFIG["VOLUME_DISPLAY"]
NOISE_REDUCTION_ENABLED = CONFIG["NOISE_REDUCTION_ENABLED"]
STT_MODEL = CONFIG["STT_MODEL"]
AI_MODEL = CONFIG["AI_MODEL"]


# ================= ENVIRONMENT CHECK =================
def check_environment():
    """Check required environment variables and play warning sounds if missing."""
    
    ENV_CHECKS = {
        "warnings": {
            "MONGODB_URI": {
                "sound": constrants.MONGODB_WARNING_SOUND,
                "message": "Continuing with default configuration (MongoDB not available)"
            }
        },
        "critical": {
            "GROQ_API_KEY": {},
            "PORCUPINE_API_KEY": {},
            "SECRET_KEY": {},
            "SPOTIFY_CLIENT_ID": {},
            "SPOTIFY_CLIENT_SECRET": {},
            "_sound": constrants.CRITICAL_ENV_VAR_SOUND
        }
    }
    
    # Check warning variables
    for var, config in ENV_CHECKS["warnings"].items():
        if not os.getenv(var):
            logger.error(f"{var} environment variable is not set")
            AudioProcessor.play_sound(config["sound"])
            logger.warning(config["message"])
    
    # Check critical variables
    missing_keys = [var for var in ENV_CHECKS["critical"] 
                   if not var.startswith("_") and not os.getenv(var)]
    
    if missing_keys:
        logger.error(f"Missing required enviroment variables: {', '.join(missing_keys)}")
        AudioProcessor.play_sound(ENV_CHECKS["critical"]["_sound"])
        logger.critical("Exiting due to missing critical enviroment variables")
        sys.exit(1)