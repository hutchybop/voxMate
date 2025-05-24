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
from ctypes import *
from gtts import gTTS
from openai import OpenAI
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Optional, Tuple, Generator

# Constants
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'
BLOCKSIZE = 16000
SILENCE_THRESHOLD = 10100
SILENCE_DURATION = 1.0
KEYWORD_PATH = '../../modelsporcupine_keywords/hey-bop_en_raspberry-pi_v3_0_0.ppn'
GENERATING_SOUND = '../../audio/generating.mp3'
GREETING_SOUND = '../../audio/greeting.mp3'
ENV_PATH = '../../.env'

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

# ALSA Error Handler Suppression (Linux-only)
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt): 
    pass

try:
    cdll.LoadLibrary('libasound.so').snd_lib_error_set_handler(ERROR_HANDLER_FUNC(py_error_handler))
except Exception as e:
    logger.debug(f"Couldn't set ALSA error handler: {e}")

class AudioProcessor:
    """Handles all audio-related operations"""
    
    @staticmethod
    def start_looping_sound() -> subprocess.Popen:
        """Start background looping sound indicating processing"""
        try:
            return subprocess.Popen(
                ["mpg321", "-q", "--loop", "-1", GENERATING_SOUND],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.PIPE  # Prevents hanging on terminate
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
        """Play a single sound file"""
        try:
            subprocess.run(
                ["mpg321", "-q", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Error playing sound {file_path}: {e}")

    @staticmethod
    def record_audio_to_file() -> str:
        """Record audio until silence is detected and save to temporary WAV file"""
        silence_start = None
        audio_data = []
        
        def callback(indata, frames, time_info, status):
            nonlocal silence_start
            if status:
                if status.input_overflow:
                    logger.warning("Input overflow in audio stream")
            
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
        except sd.PortAudioError as e:
            logger.error(f"Audio device error: {e}")
            raise
        except Exception as e:
            logger.error(f"Recording error: {e}")
            raise

        # Save to temp WAV file
        temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        try:
            with wave.open(temp_audio.name, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(SAMPLE_RATE)
                for chunk in audio_data:
                    wf.writeframes(chunk.tobytes())
            return temp_audio.name
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            os.unlink(temp_audio.name)
            raise

class AIService:
    """Handles all AI-related operations"""
    
    def __init__(self):
        load_dotenv(ENV_PATH)
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.access_key = os.getenv("PORCUPINE_API_KEY")
        
        if not self.access_key:
            logger.error("Porcupine API key not found in environment variables")
            raise ValueError("Missing API keys")

    def transcribe_audio(self, audio_path: str) -> Tuple[str, float, subprocess.Popen]:
        """Transcribe audio using Whisper API"""
        sound_process = AudioProcessor.start_looping_sound()
        start_time = time.time()
        
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
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
                model="mistral-saba-24b",
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
    logger.info("Listening for wake word... (say 'Hey Bop')")
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

    try:
        ai_service = AIService()
        
        with audio_wake_stream(ai_service.access_key) as (porcupine, pa, stream):
            while True:
                try:
                    # Wake word detection phase
                    wake_word_detection(porcupine, stream)
                    
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
                        logger.info(f"- STT Processing: {stt_time:.2f}s")
                        logger.info(f"- STT & Playback: {total_stt:.2f}s")
                        logger.info(f"- AI Response: {ai_time:.2f}s")
                        logger.info(f"- TTS Generation: {tts_time:.2f}s")
                        logger.info(f"- TTS & Playback: {total_tts:.2f}s")

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
