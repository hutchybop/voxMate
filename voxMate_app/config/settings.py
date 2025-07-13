# Required python imports
import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.database import Database

# Required local imports
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
    if (mongodb := load_mongodb()) is None:
        return None  # Connection error already logged

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
def check_environment(audio_player=None):
    """Check environment variables with optional audio feedback"""
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
    
    # Check warnings
    for var, config in ENV_CHECKS["warnings"].items():
        if not os.getenv(var):
            logger.error(f"{var} environment variable is not set")
            if audio_player:  # Only play sound if player is provided
                audio_player.play_sound(config["sound"])
            logger.warning(config["message"])
    
    # Check critical
    missing_keys = [var for var in ENV_CHECKS["critical"] 
                   if not var.startswith("_") and not os.getenv(var)]
    
    if missing_keys:
        logger.error(f"Missing required environment variables: {', '.join(missing_keys)}")
        if audio_player:
            audio_player.play_sound(ENV_CHECKS["critical"]["_sound"])
        logger.critical("Exiting due to missing critical environment variables")
        sys.exit(1)