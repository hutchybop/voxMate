import pyaudio
import numpy as np
import time

CHUNK = 1024
RATE = 16000
SILENCE_THRESHOLD = 2500 # Set for mic being used
SILENCE_DURATION = 2.0

def is_silent(data_chunk):
    audio_data = np.frombuffer(data_chunk, dtype=np.int16)
    volume = np.linalg.norm(audio_data)
    print(f"Volume: {volume:.2f}")
    return volume < SILENCE_THRESHOLD

def listen_for_silence():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print("Listening for Voice...")

    silence_start = None

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)

            if is_silent(data):
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_DURATION:
                    print(f"End of question detected ({SILENCE_DURATION} seconds, silence)")
                    break
            
            else:
                silence_start = None
        
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

try:
    listen_for_silence()
except KeyboardInterrupt:
    print("\nInterrupted by user, exiting cleanly.")