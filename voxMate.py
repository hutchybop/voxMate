import os
import queue
import re
import struct
import signal
import atexit
import sys
import tempfile
import time
import subprocess
import logging
import numpy as np
import sounddevice as sd
import pvporcupine
import pyaudio
from ctypes import *
from gtts import gTTS
from openai import OpenAI
from dotenv import load_dotenv
from contextlib import contextmanager

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# ALSA Error Handler Suppression (Linux-only)
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt): pass
try:
    cdll.LoadLibrary('libasound.so').snd_lib_error_set_handler(ERROR_HANDLER_FUNC(py_error_handler))
except Exception: pass

# Constants
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'
BLOCKSIZE = 16000
SILENCE_THRESHOLD = 2600
SILENCE_DURATION = 1.5

audio_queue = queue.Queue()

# Load environment and OpenAI client
load_dotenv("../../.env")
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("OPENAI_API_KEY"))
access_key = os.getenv("PORCUPINE_API_KEY")

# Global flag
cleanup_done = False

# Context Manager for Porcupine + PyAudio
@contextmanager
def audio_wake_stream():
    pa = pyaudio.PyAudio()
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=['../../models/porcupine_keywords/hey-bop_en_raspberry-pi_v3_0_0.ppn']
    )
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )
    try:
        yield porcupine, pa, stream
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

def start_looping_sound():
    return subprocess.Popen(
        ["mpg321", "-q", "--loop", "-1", "../../audio/generating.mp3"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def stop_looping_sound(process):
    if process and process.poll() is None:
        process.terminate()

def wake_word(porcupine, stream):
    logging.info("Listening for wake word... (say 'Hey Bop')")
    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        if porcupine.process(pcm) >= 0:
            logging.info("Wake word detected!")
            subprocess.run(["mpg321", "-q", "../../audio/greeting.mp3"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            break

def record_audio_to_file():
    # Record audio to temporary WAV file for Whisper
    print("\nRecording, what do you want to say?")
    
    # Create temp file
    temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

    silence_start = None
    audio_data = []
    
    def callback(indata, frames, time_info, status):
        nonlocal silence_start, audio_data
        if status and status.input_overflow:
            print("Input overflow")
        
        audio_chunk = indata.copy()
        volume = np.linalg.norm(audio_chunk)
        audio_data.append(audio_chunk)

        if volume < SILENCE_THRESHOLD:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start > SILENCE_DURATION:
                raise sd.CallbackStop()
        else:
            silence_start = None

    try:
        stream = sd.InputStream(samplerate=SAMPLE_RATE, dtype=DTYPE, channels=CHANNELS, callback=callback)
        try:
            stream.start()
            while stream.active:
                time.sleep(0.1)  # Small sleep to avoid busy-waiting
        except sd.CallbackStop:
            pass
        finally:
            stream.stop()
            stream.close()
    except sd.CallbackStop:
        pass
        
    # Convert raw audio to WAV format
    import wave
    with wave.open(temp_audio.name, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        for chunk in audio_data:
            wf.writeframes(chunk.tobytes())
    
    return temp_audio.name

def transcribe_with_whisper(audio_path):
    sound_process = start_looping_sound()
    start_time = time.time()
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=audio_file,
                language="en",
                response_format="text"
            )
        if transcript:
            logging.info(f"You asked: {transcript.strip()}")
        return transcript.strip(), time.time() - start_time, sound_process
    finally:
        os.unlink(audio_path)

def ai_call(prompt):
    try:
        response = client.chat.completions.create(
            model="mistral-saba-24b",
            messages=[
                {"role": "system", "content": "You are a helpful smart speaker assistant. Avoid lists and give answers in concise brief sentences."},
                {"role": "user", "content": f"Answer very briefly: {prompt}"}
            ],
            max_tokens=100, temperature=0.7
        )
        message = response.choices[0].message.content
        logging.info(f"AI Response: {message}")
        return re.sub(r"<think>.*?</think>", "", message, flags=re.DOTALL).strip()
    except Exception as e:
        logging.error(f"API Error: {e}")
        return "Sorry, I encountered an error."

def text_to_speech(message, sound_process):
    if not message: return 0
    start_time = time.time()
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as f:
            gTTS(text=re.sub(r"[_*~]", "", message), lang='en').save(f.name)
            stop_looping_sound(sound_process)
            stop_time = time.time()
            subprocess.run(["mpg321", "-q", f.name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logging.error(f"TTS Error: {e}")
    return stop_time - start_time

def cleanup():
    global cleanup_done
    if cleanup_done:
        return
    cleanup_done = True
    logging.info("Cleanup complete.")

signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
atexit.register(cleanup)

# Main loop
if __name__ == "__main__":
    try:
        with audio_wake_stream() as (porcupine, pa, stream):
            while True:
                wake_word(porcupine, stream)
                start_total = time.time()
                audio_file = record_audio_to_file()
                transcript, stt_time, sound_process = transcribe_with_whisper(audio_file)
                total_stt = time.time() - start_total

                if transcript:
                    ai_start = time.time()
                    ai_response = ai_call(transcript)
                    ai_time = time.time() - ai_start

                    tts_start = time.time()
                    tts_time = text_to_speech(ai_response, sound_process)
                    total_tts = time.time() - tts_start

                    logging.info(f"\nPerformance Metrics:")
                    logging.info(f"- STT Processing: {stt_time:.2f}s")
                    logging.info(f"- STT & Playback: {total_stt:.2f}s")
                    logging.info(f"- AI Response: {ai_time:.2f}s")
                    logging.info(f"- TTS Generation: {tts_time:.2f}s")
                    logging.info(f"- TTS & Playback: {total_tts:.2f}s")

    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        cleanup()
