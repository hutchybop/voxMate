# Required python imports
import logging
from ctypes import *
from dotenv import load_dotenv


# ================= INITIALIZATION =================
#Load env
load_dotenv('../../.env')

# Setup logging with more detailed format

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/smart_speaker.log')
    ]
)
logger = logging.getLogger(__name__)


# DEBUGGING: Commented out due to Seg error, moved to separate file and called in services.audio.py
# # ALSA Error Handler Supression (Linux-only)
# ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
# def py_error_handler(filename, line, function, err, fmt): 
#     pass
# try:
#     cdll.LoadLibrary('libasound.so').snd_lib_error_set_handler(ERROR_HANDLER_FUNC(py_error_handler))
# except Exception as e:
#     logger.debug(f"Couldn't set ALSA error handler: {e}")