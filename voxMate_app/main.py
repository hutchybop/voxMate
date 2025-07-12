#!/usr/bin/env python3

# Required python imports
import signal
import atexit
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Loading env variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Required local imports
from utils.cleanup import cleanup
from interfaces.socketio import sio
from utils.logging import logger
from services.audio import AudioProcessor
from services.ai import AIService
import config.settings as settings
import services.wakeword as wakeword
from utils.state import app_state
from services.spotify_app import SpotifyPlayer

def main() -> None:
    """Main execution loop"""
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    atexit.register(cleanup)

    # Check environment variables before proceeding
    settings.check_environment()

    # Connect to Socket.IO server (non-blocking)
    try:
        sio.connect('http://localhost:5000', wait_timeout=10)
        logger.info("Listening for settings updates...")
    except Exception as e:
        # Continue running even if Socket.IO fails
        logger.warning(f"Could not connect to Socket.IO server: {e}")
        
    try:    
        ai_service = AIService()
        logger.info(f"Noise reduction: {'ENABLED' if settings.NOISE_REDUCTION_ENABLED else 'DISABLED'}")
        logger.info(f"Volume Display: {'ENABLED' if settings.VOLUME_DISPLAY else 'DISABLED'}")
        
        while True:
            try:
                app_state.set_state("WAITING")

                # Wake word phase (PyAudio holds mic)
                with wakeword.audio_wake_stream(ai_service.access_key) as (porcupine, pa, stream):
                    wakeword.wake_word_detection(porcupine, stream)

                # Mic now released — record using sounddevice
                app_state.set_state("PROCESSING")

                start_total = time.time()
                audio_file = AudioProcessor.record_audio_to_file()
                transcript, stt_time, sound_process = ai_service.transcribe_audio(audio_file)
                total_stt = time.time() - start_total

                if transcript:
                    # AI response generation
                    ai_start = time.time()
                    ai_response, play_spotify = ai_service.generate_response(transcript)
                    ai_time = time.time() - ai_start

                    # Text-to-speech
                    tts_start = time.time()
                    tts_time = ai_service.text_to_speech(ai_response, sound_process)
                    total_tts = time.time() - tts_start

                    if play_spotify is not None:
                        spotify_player = SpotifyPlayer()
                        if not spotify_player.handle_spotify_play(play_spotify.get("params")):
                            logger.error("Failed to play Spotify content")

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