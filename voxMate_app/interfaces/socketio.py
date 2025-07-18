# Required python imports
import socketio

# Required local imports
from utils.logging import logger
from config.settings import load_config
import config.constrants as constrants
from utils.state import app_state


# ================= SOCKET IO =================
sio = socketio.Client()

@sio.event
def connect():
    logger.info("Connected to server")

@sio.event
def disconnect():
    logger.warning("Disconnected to server")


# Update config if socketio recieved
@sio.on('settings_updated')
def on_settings_updated():
    """Handle settings updates with state awareness"""
    logger.info("Received updated voxMate settings")

    try:
        global CONFIG, SILENCE_THRESHOLD, SILENCE_DURATION, VOLUME_DISPLAY, NOISE_REDUCTION_ENABLED, STT_MODEL, AI_MODEL
        CONFIG = load_config()
        SILENCE_THRESHOLD = CONFIG["SILENCE_THRESHOLD"]
        SILENCE_DURATION = CONFIG["SILENCE_DURATION"]
        VOLUME_DISPLAY = CONFIG["VOLUME_DISPLAY"]
        NOISE_REDUCTION_ENABLED = CONFIG["NOISE_REDUCTION_ENABLED"]
        STT_MODEL = CONFIG["STT_MODEL"]
        AI_MODEL = CONFIG["AI_MODEL"]
    finally:
        logger.info(f"Noise reduction: {'ENABLED' if NOISE_REDUCTION_ENABLED else 'DISABLED'}")
        logger.info(f"Volume Display: {'ENABLED' if VOLUME_DISPLAY else 'DISABLED'}")
        if app_state.is_waiting():
            logger.info(f"Listening for wake word... (say '{constrants.WAKE_WORD}')")