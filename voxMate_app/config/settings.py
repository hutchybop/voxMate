# Required python imports
import os
import json
import sys
from pathlib import Path
from typing import Dict, Any
from pymongo import MongoClient

# Required local imports
from services.audio import AudioProcessor
from utils.logging import logger


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


def load_config() -> Dict[str, Any]:
    """Load configuration from user file and MongoDB with fallbacks."""
    # Load user config if exists
    config_path = Path(__file__).resolve().parent / "config" / "user_config.json"
    user_config = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            user_config = json.load(f)

    # Try to connect to MongoDB if URI is available
    mongodb_uri = os.getenv("MONGODB_URI")

    if mongodb_uri:
        try:
            mongodb = MongoClient(mongodb_uri).get_default_database()
            
            # Try user settings first, then fall back to default settings
            settings = mongodb.appSettings.find_one({"_id": user_config.get("user_id")}) or {}

            if not settings:
                settings = mongodb.appSettings.find_one({"_id": "default"}) or {}

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
            logger.warning("Using default configuration")

    # Fallback to defaults if MongoDB not available
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
def check_environment():
    """Check required environment variables and play warning sounds if missing."""
    
    ENV_CHECKS = {
        "warnings": {
            "MONGODB_URI": {
                "sound": "audio/warning_mongodb.mp3",
                "message": "Continuing with default configuration (MongoDB not available)"
            }
        },
        "critical": {
            "GROQ_API_KEY": {},
            "PORCUPINE_API_KEY": {},
            "SECRET_KEY": {},
            "SPOTIFY_CLIENT_ID": {},
            "SPOTIFY_CLIENT_SECRET": {},
            "_sound": "audio/critical_env_var.mp3"
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