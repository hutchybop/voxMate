# Required python imports
import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.database import Database
import pyaudio

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
    "AI_MODEL": "mistral-saba-24b",
    "MIC_DEVICE_INDEX": None
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

def find_input_device(
    pa: pyaudio.PyAudio,
    mongodb: Optional[Database],
    user_id: str,
    name_substring="seeed2",
    channels_required=constrants.CHANNELS,
    device_index: Optional[int] = None
) -> int:
    try:
        if device_index is not None:
            try:
                info = pa.get_device_info_by_index(device_index)
                if info["maxInputChannels"] >= channels_required:
                    logger.info(f"Using valid stored input device: {info['name']} (index {device_index})")
                    return device_index
                else:
                    logger.warning(f"Stored device index {device_index} does not support enough channels")
            except Exception as e:
                logger.warning(f"Stored device index {device_index} is invalid or unavailable: {e}")
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info["maxInputChannels"] >= channels_required and name_substring.lower() in info["name"].lower():
                logger.info(f"Found matching input device: {info['name']} (index {i})")
                if mongodb:
                    try:
                        mongodb.appSettings.update_one(
                            {"user_id": user_id},
                            {"$set": {"mic_device_index": i}},
                            upsert=True
                        )
                        logger.info(f"Saved new mic device index {i} to DB")
                    except Exception as db_err:
                        logger.error(f"Failed to update mic index in DB: {db_err}")
                else:
                    logger.warning("MongoDB not available — mic index not saved")
                return i
        logger.critical(f"No valid mic input device found containing '{name_substring}' with at least {channels_required} channels.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error during mic device detection: {e}")
        sys.exit(1)
        
        

def load_config() -> Dict[str, Any]:
    """Load configuration from user file and MongoDB with fallbacks."""
    user_config = load_user()
    user_id = user_config.get("user_id") if user_config else None
    pa = pyaudio.PyAudio()
    mongodb = load_mongodb()
    settings = DEFAULT_CONFIG.copy()  # Always copy to avoid mutating global
    db_mic_index = None  # Initialize here to use in fallback too
    try:
        if mongodb and user_id:
            # Try user settings first, then fall back to default in DB
            user_settings = mongodb.appSettings.find_one({"user_id": user_id}) or {}
            if not user_settings:
                user_settings = mongodb.appSettings.find_one({"user_id": "default"}) or {}
            settings.update(user_settings)  # Merge with DEFAULT_CONFIG
            db_mic_index = user_settings.get("mic_device_index")
        # Validate or detect mic index
        mic_index = find_input_device(pa, mongodb, user_id or "unknown", "seeed2", constrants.CHANNELS, db_mic_index)
        logger.info("User config settings loaded")
        # Final merged config
        return {
            "SILENCE_THRESHOLD": settings.get('silence_threshold', DEFAULT_CONFIG["SILENCE_THRESHOLD"]),
            "SILENCE_DURATION": settings.get('silence_duration', DEFAULT_CONFIG["SILENCE_DURATION"]),
            "VOLUME_DISPLAY": settings.get('volume_display', DEFAULT_CONFIG["VOLUME_DISPLAY"]),
            "NOISE_REDUCTION_ENABLED": settings.get('noise_reduction', DEFAULT_CONFIG["NOISE_REDUCTION_ENABLED"]),
            "STT_MODEL": settings.get('stt_model', DEFAULT_CONFIG["STT_MODEL"]),
            "AI_MODEL": settings.get('ai_model', DEFAULT_CONFIG["AI_MODEL"]),
            "MIC_DEVICE_INDEX": mic_index
        }
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB or load config: {e}")
        logger.warning("Using default configuration")
        mic_index = find_input_device(pa, None, user_id or "unknown", "seeed2", constrants.CHANNELS)
        fallback_config = DEFAULT_CONFIG.copy()
        fallback_config["MIC_DEVICE_INDEX"] = mic_index
        return fallback_config


# Load configuration when module is imported
CONFIG = load_config()

# Make settings available as module-level constants
SILENCE_THRESHOLD = CONFIG["SILENCE_THRESHOLD"]
SILENCE_DURATION = CONFIG["SILENCE_DURATION"]
VOLUME_DISPLAY = CONFIG["VOLUME_DISPLAY"]
NOISE_REDUCTION_ENABLED = CONFIG["NOISE_REDUCTION_ENABLED"]
STT_MODEL = CONFIG["STT_MODEL"]
AI_MODEL = CONFIG["AI_MODEL"]
MIC_DEVICE_INDEX = CONFIG["MIC_DEVICE_INDEX"]


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