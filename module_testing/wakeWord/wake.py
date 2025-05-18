# Need to create an account with porcupine, then create a keyword if wanted.

import pvporcupine
import pyaudio
import struct
import os
from dotenv import load_dotenv
import sys
from ctypes import *

# ALSA error handler
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
try:
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass  # Skip if not on Linux

load_dotenv("../../.env")
access_key = os.getenv("PORCUPINE_API_KEY")

# Initialize Porcupine
porcupine = pvporcupine.create(access_key=access_key, keyword_paths=['../../models/porcupine_keywords/hey-bop_en_raspberry-pi_v3_0_0.ppn'])

# Initialize PyAudio with suppressed errors
with open(os.devnull, 'w') as devnull:
    old_stderr = os.dup(sys.stderr.fileno())
    os.dup2(devnull.fileno(), sys.stderr.fileno())
    
    pa = pyaudio.PyAudio()
    
    os.dup2(old_stderr, sys.stderr.fileno())

stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length,
)

print("Listening for wake word... (say 'Hey Bop')")

try:
    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("Wake word detected!")

except KeyboardInterrupt:
    print("Stopping...")

finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
    porcupine.delete()
