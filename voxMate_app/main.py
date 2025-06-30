#!/usr/bin/env python3

print("🟢 Starting main.py")

print("📦 Importing Path")
from pathlib import Path

# Loading env
print("📦 Loading env variables")
from dotenv import load_dotenv
# Automatically load the .env from the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Required python imports
print("📦 Importing signal")
import signal

print("📦 Importing atexit")
import atexit

print("📦 Importing sys")
import sys

print("📦 Importing time")
import time

# Required local imports
print("📦 Importing cleanup from utils.cleanup")
from utils.cleanup import cleanup

print("📦 Importing sio from interfaces.socketio")
from interfaces.socketio import sio

print("📦 Importing logger from utils.logging")
from utils.logging import logger

print("📦 Importing AudioProcessor from services.audio")
from services.audio import AudioProcessor

print("📦 Importing AIService from services.ai")
from services.ai import AIService

print("📦 Importing settings from config.settings")
import config.settings as settings

print("📦 Importing wakeword from services.wakeword")
import services.wakeword as wakeword

print("📦 Importing app_state from utils.state")
from utils.state import app_state

print("✅ All imports completed successfully.")

def main() -> None:
    print("🚀 main() started")
    
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    atexit.register(cleanup)

    print("🔍 Checking environment variables")
    settings.check_environment()

    print("🔗 Attempting to connect to Socket.IO server")
    try:
        sio.connect('http://localhost:5000', wait_timeout=10)
        logger.info("Listening for settings updates...")
    except Exception as e:
        logger.warning(f"Could not connect to Socket.IO server: {e}")
        
    try:    
        print("🧠 Initializing AIService")
        ai_service = AIService()
        logger.info(f"Noise reduction: {'ENABLED' if settings.NOISE_REDUCTION_ENABLED else 'DISABLED'}")
        logger.info(f"Volume Display: {'ENABLED' if settings.VOLUME_DISPLAY else 'DISABLED'}")

        print("🎤 Starting audio wake stream")
        with wakeword.audio_wake_stream(ai_service.access_key) as (porcupine, pa, stream):
            while True:
                try:
                    app_state.set_state("WAITING")
                    wakeword.wake_word_detection(porcupine, stream)

                    app_state.set_state("PROCESSING")
                    logger.info("Wake word detected! Ask your question...")

                    start_total = time.time()
                    audio_file = AudioProcessor.record_audio_to_file()
                    transcript, stt_time, sound_process = ai_service.transcribe_audio(audio_file)
                    total_stt = time.time() - start_total

                    if transcript:
                        ai_start = time.time()
                        ai_response = ai_service.generate_response(transcript)
                        ai_time = time.time() - ai_start

                        tts_start = time.time()
                        tts_time = ai_service.text_to_speech(ai_response, sound_process)
                        total_tts = time.time() - tts_start

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
    print("👟 Running __main__")
    main()