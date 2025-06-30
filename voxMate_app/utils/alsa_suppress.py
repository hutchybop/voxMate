# Required python import
from ctypes import *

# Required local import
# from utils.logging import logger

# ALSA Error Handler Supression (Linux-only)
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt): 
    pass

def suppress_alsa_errors():
    try:
        cdll.LoadLibrary('libasound.so').snd_lib_error_set_handler(ERROR_HANDLER_FUNC(py_error_handler))
    except Exception:
        # logger.debug(f"Couldn't set ALSA error handler: {e}")
        pass