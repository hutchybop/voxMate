#!/usr/bin/env python3
import os
import re
import struct
import signal
import atexit
import sys
import tempfile
import time
import subprocess
import wave
import logging
import numpy as np
import sounddevice as sd
import pvporcupine
import pyaudio
import socketio
import threading
from ctypes import *
from gtts import gTTS
from openai import OpenAI
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Optional, Tuple, Generator
from pymongo import MongoClient
import json
from pathlib import Path
from typing import Dict, Any


# ================= INITIALIZATION =================
#Load env
load_dotenv()

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

# ALSA Error Handler Supression (Linux-only)
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt): 
    pass
try:
    cdll.LoadLibrary('libasound.so').snd_lib_error_set_handler(ERROR_HANDLER_FUNC(py_error_handler))
except Exception as e:
    logger.debug(f"Couldn't set ALSA error handler: {e}")

# Improved state tracking with thread safety
class AppState:
    """Thread-safe application state management"""
    _states = {
        "WAITING": "Waiting for wake word",
        "PROCESSING": "Processing response"
    }

    def __init__(self):
        self._state = "WAITING"
        self._lock = threading.Lock()

    @property
    def state(self):
        with self._lock:
            return self._state

    def set_state(self, new_state):
        with self._lock:
            if new_state in self._states:
                old_state = self._state
                self._state = new_state
                logger.debug(f"State changed: {old_state} → {new_state}")
            else:
                raise ValueError(f"Invalid state: {new_state}")
            
    def is_waiting(self):
        return self.state == "WAITING"

# Global state instance
app_state = AppState()


# ================= SOCKET IO =================
sio = socketio.Client()

@sio.event
def connect():
    logger.info("socket.IO connected to server")

@sio.event
def disconnect():
    logger.warning("socket.IO disconnected to server")
    

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
            logger.info(f"Listening for wake word... (say '{WAKE_WORD}')")


# Make settings available as module-level constants
SILENCE_THRESHOLD = CONFIG["SILENCE_THRESHOLD"]
SILENCE_DURATION = CONFIG["SILENCE_DURATION"]
VOLUME_DISPLAY = CONFIG["VOLUME_DISPLAY"]
NOISE_REDUCTION_ENABLED = CONFIG["NOISE_REDUCTION_ENABLED"]
STT_MODEL = CONFIG["STT_MODEL"]
AI_MODEL = CONFIG["AI_MODEL"]

# Other default variables
SAMPLE_RATE = 16000
CHANNELS = 2
DTYPE = 'int16'
BLOCKSIZE = 16000
WAKE_WORD = 'Hey VoxMate'

# Paths
# Get absolute path to be safe
KEYWORD_PATH = Path(__file__).resolve().parent / "models" / "porcupine_keywords" / os.getenv("PORCUPINE_KEYWORD_FILE_NAME")
GENERATING_SOUND = 'audio/generating.mp3'
GREETING_SOUND = 'audio/greeting.mp3'


class AudioProcessor:
    """Handles all audio operations with configurable noise reduction"""
    @staticmethod
    def start_looping_sound() -> subprocess.Popen:
        try:
            return subprocess.Popen(
                ["mpg321", "-o", "pulse", "--stereo", "-q", "--loop", "-1", GENERATING_SOUND],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.PIPE   # Prevents hanging on terminate
            )
        except FileNotFoundError:
            logger.error("mpg321 not found. Please install mpg321 for audio playback.")
            raise

    @staticmethod
    def stop_looping_sound(process: Optional[subprocess.Popen]) -> None:
        """Stop the background looping sound"""
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping sound process: {e}")

    @staticmethod
    def play_sound(file_path: str) -> None:
        """Play sound with explicit stereo output"""
        try:
            result = subprocess.run(
                ["mpg321", "-o", "pulse", "--stereo", "-q", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,  # Capture stderr for debugging
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Error playing sound {file_path}: {e.stderr.decode().strip()}")
            # Fallback to non-stereo mode if needed
            try:
                subprocess.run(
                    ["mpg321", "-o", "pulse", "-q", file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
            except subprocess.CalledProcessError as fallback_e:
                logger.error(f"Fallback playback failed: {fallback_e}")

    @staticmethod
    def record_audio_to_file() -> str:
        """Record audio until silence is detected and save to temporary WAV file"""
        silence_start = None
        audio_data = []
        consecutive_silent_chunks = 0
        
        def callback(indata, frames, time_info, status):
            nonlocal silence_start, consecutive_silent_chunks
            if status and status.input_overflow:
                logger.warning("Input overflow in audio stream detected")
            
            chunk = indata.copy()
            volume = np.linalg.norm(chunk)

            # Shows volume in terminal while mic is in use if set to true
            if VOLUME_DISPLAY:
                print(f"Mic Volume detected: {volume}")

            
            if NOISE_REDUCTION_ENABLED:
                if volume > SILENCE_THRESHOLD:
                    audio_data.append(chunk)
                    consecutive_silent_chunks = 0
                elif audio_data:
                    consecutive_silent_chunks += 1
                    if consecutive_silent_chunks > int(SILENCE_DURATION * SAMPLE_RATE / BLOCKSIZE):
                        raise sd.CallbackStop()
            else:
                audio_data.append(chunk)
                if volume < SILENCE_THRESHOLD:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > SILENCE_DURATION:
                        raise sd.CallbackStop()
                else:
                    silence_start = None

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                dtype=DTYPE,
                channels=CHANNELS,
                callback=callback,
                blocksize=BLOCKSIZE
            ) as stream:
                logger.info("\nRecording... (speak now)")
                while stream.active:
                    time.sleep(0.1)

            # Save to temp WAV file
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            with wave.open(temp_audio.name, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(SAMPLE_RATE)
                for chunk in audio_data:
                    wf.writeframes(chunk.tobytes())
            
            logger.debug(f"Recorded {len(audio_data)} chunks (Noise reduction: {'ON' if NOISE_REDUCTION_ENABLED else 'OFF'})")
            return temp_audio.name
            
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            os.unlink(temp_audio.name)
            raise

class AIService:
    """Handles all AI-related operations"""
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.access_key = os.getenv("PORCUPINE_API_KEY")

        if not self.access_key:
            logger.error("Porcupine API key not found in environment variables")
            raise ValueError("Missing API key")
        
    def transcribe_audio(self, audio_path: str) -> Tuple[str, float, subprocess.Popen]:
        """Transcribe audio using Whisper API"""
        sound_process = AudioProcessor.start_looping_sound()
        start_time = time.time()

        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=STT_MODEL,
                    file=audio_file,
                    language="en",
                    response_format="text"
                )

            if transcript:
                logger.info(f"Transcription: {transcript.strip()}")
            return transcript.strip(), time.time() - start_time, sound_process
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            AudioProcessor.stop_looping_sound(sound_process)
            raise
        finally:
            try:
                os.unlink(audio_path)
            except Exception as e:
                logger.error(f"Error deleting temp audio file: {e}")

    def generate_response(self, prompt: str) -> str:
        """Generate AI response using chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful smart speaker assistant. "
                                  "Avoid lists and give answers in concise brief sentences."
                    },
                    {
                        "role": "user",
                        "content": f"Answer very briefly: {prompt}"
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )
            message = response.choices[0].message.content
            logger.info(f"AI Response: {message}")
            # Remove any special formatting tags
            return re.sub(r"<think>.*?</think>", "", message, flags=re.DOTALL).strip()
        except Exception as e:
            logger.error(f"AI API Error: {e}")
            return "Sorry, I encountered an error processing your request."

    def text_to_speech(self, message: str, sound_process: Optional[subprocess.Popen]) -> float:
        """Convert text to speech and play it"""
        if not message:
            return 0
        
        start_time = time.time()

        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as f:
                # Clean special characters that might cause TTS issues
                clean_text = re.sub(r"[_*~]", "", message)
                gTTS(text=clean_text, lang='en').save(f.name)
                AudioProcessor.stop_looping_sound(sound_process)
                stop_time = time.time()
                AudioProcessor.play_sound(f.name)
                return stop_time - start_time
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return 0

@contextmanager
def audio_wake_stream(access_key: str) -> Generator[Tuple[pvporcupine.Porcupine, pyaudio.PyAudio, pyaudio.Stream], None, None]:
    """Context manager for Porcupine wake word detection"""
    pa = None
    porcupine = None
    stream = None

    try:
        pa = pyaudio.PyAudio()
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[KEYWORD_PATH]
        )
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )
        yield porcupine, pa, stream
    except Exception as e:
        logger.error(f"Error initializing audio wake stream: {e}")
        raise
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        if pa:
            pa.terminate()
        if porcupine:
            porcupine.delete()

def wake_word_detection(porcupine: pvporcupine.Porcupine, stream: pyaudio.Stream) -> None:
    """Listen for wake word and respond when detected"""
    logger.info(f"Listening for wake word... (say '{WAKE_WORD}')")
    while True:
        try:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            if porcupine.process(pcm) >= 0:
                logger.info("Wake word detected!")
                AudioProcessor.play_sound(GREETING_SOUND)
                break
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            raise

def cleanup() -> None:
    """Cleanup resources before exit"""
    if hasattr(cleanup, '_called'):
        return
    cleanup._called = True
    logger.info("Performing cleanup...")
    # Add any additional cleanup needed here

def main() -> None:
    """Main execution loop"""
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    atexit.register(cleanup)

    # Check environment variables before proceeding
    check_environment()

    # Connect to Socket.IO server (non-blocking)
    try:
        sio.connect('http://localhost:5000', wait_timeout=10)
        logger.info("Listening for settings updates...")
    except Exception as e:
        # Continue running even if Socket.IO fails
        logger.warning(f"Could not connect to Socket.IO server: {e}")
        
    try:    
        ai_service = AIService()
        logger.info(f"Noise reduction: {'ENABLED' if NOISE_REDUCTION_ENABLED else 'DISABLED'}")
        logger.info(f"Volume Display: {'ENABLED' if VOLUME_DISPLAY else 'DISABLED'}")
        
        with audio_wake_stream(ai_service.access_key) as (porcupine, pa, stream):
            while True:
                try:
                    # Update state to waiting for wake word
                    app_state.set_state("WAITING")

                    # Wake word detection phase
                    wake_word_detection(porcupine, stream)

                    # Update state to processing question
                    app_state.set_state("PROCESSING")
                    logger.info("Wake word detected! Ask your question...")

                    # Recording and processing phase
                    start_total = time.time()
                    audio_file = AudioProcessor.record_audio_to_file()
                    transcript, stt_time, sound_process = ai_service.transcribe_audio(audio_file)
                    total_stt = time.time() - start_total

                    if transcript:
                        # AI response generation
                        ai_start = time.time()
                        ai_response = ai_service.generate_response(transcript)
                        ai_time = time.time() - ai_start

                        # Text-to-speech conversion
                        tts_start = time.time()
                        tts_time = ai_service.text_to_speech(ai_response, sound_process)
                        total_tts = time.time() - tts_start

                        # Performance metrics
                        logger.info("\nPerformance Metrics:")
                        logger.info(f"STT Processing: {stt_time:.2f}s")
                        logger.info(f"STT & Playback: {total_stt:.2f}s")
                        logger.info(f"AI Response: {ai_time:.2f}s")
                        logger.info(f"TTS Generation: {tts_time:.2f}s")
                        logger.info(f"TTS & Playback: {total_tts:.2f}s")

                except KeyboardInterrupt:
                    logger.info("Interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(2)
                    continue

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()