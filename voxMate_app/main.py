#!/usr/bin/env python3

# Required python imports
import signal
import atexit
import sys
import time
import os
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
from actions.dispatcher import handle_cmd
from utils.mic_lights import MicLights

def main() -> None:
    """Main execution loop"""
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    # Initialize services
    audio = AudioProcessor()
    atexit.register(cleanup)
    lights = MicLights()

    # Check environment variables before proceeding  
    settings.check_environment(audio_player=audio)

    # Connect to Socket.IO server (non-blocking)
    try:
        sio.connect('http://localhost:5000', wait_timeout=10)
        logger.info("Listening for settings updates...")
    except Exception as e:
        # Continue running even if Socket.IO fails
        logger.warning(f"[main] Could not connect to Socket.IO server: {e}")
        
    try:    
        ai_service = AIService()
        logger.info(f"Noise reduction: {'ENABLED' if settings.NOISE_REDUCTION_ENABLED else 'DISABLED'}")
        logger.info(f"Volume Display: {'ENABLED' if settings.VOLUME_DISPLAY else 'DISABLED'}")
        
        while True:
            try:

                if os.getenv("remote") == "false":

                    app_state.set_state("status", "waiting")
                    lights.lights_idle()

                    # Wake word phase (PyAudio holds mic)
                    with wakeword.audio_wake_stream(ai_service.access_key) as (porcupine, pa, stream):
                        wakeword.wake_word_detection(porcupine, stream, lights)

                    # Mic now released — record using sounddevice
                    app_state.set_state("status", "processing")
                    lights.lights_listening()

                    start_total = time.time()
                    audio_file = AudioProcessor.record_audio_to_file()
                    success = False

                    
                    lights.lights_pulsing_processing()

                    transcript, stt_time = ai_service.transcribe_audio(audio_file)
                    total_stt = time.time() - start_total

                else: 
                    transcript = input("{\"response\":\"Playing Thunderstruck by AC/DC.\",\"action\":\"spotify_play\",\"query\":\"Thunderstruck\",\"artist\":\"AC/DC\",\"type\":\"track\"}")

                if transcript:
                    # AI response generation
                    ai_start = time.time()
                    try:
                        response_text, parsed = ai_service.generate_response(transcript)
                        if not isinstance(response_text, str):
                            response_text = str(response_text)
                    except Exception as e:
                        logger.error(f"AI processing failed: {e}")
                        response_text = "Sorry, I encountered an error processing your request"
                        parsed = None
                    ai_time = time.time() - ai_start

                    # Handle the user command and play response
                    try:
                        tts_start = time.time()
                        if parsed is not None and parsed.get("action"):
                            success, message = handle_cmd(parsed)
                            if not success and message:
                                ai_service.text_to_speech(message)
                        else:
                            tts_time = ai_service.text_to_speech(response_text)
                        total_tts = time.time() - tts_start
                    except Exception as e:
                        logger.error(f'Main loop error, processing user command: {e}')

                    # Performance metrics
                    logger.info("\nPerformance Metrics:")
                    logger.info(f"STT Processing: {stt_time:.2f}s")
                    logger.info(f"STT & Playback: {total_stt:.2f}s")
                    logger.info(f"AI Response: {ai_time:.2f}s")
                    logger.info(f"TTS Generation: {tts_time:.2f}s")
                    logger.info(f"TTS & Playback: {total_tts:.2f}s")
                else:
                    # Fall back if no recording
                    logger.warning("No sound recorded")
                    no_recoding_response = "Nothing heard, sleeping"
                    ai_service.text_to_speech(no_recoding_response)

                try:
                    # Resume Spotify play if paused
                    if app_state.is_spotify_paused():
                        success, message = handle_cmd({"cmd": "spotify_play"})
                        if not success and message:
                            ai_service.text_to_speech(message)
                except Exception as e:
                    logger.error(f'Main loop error, re-starting Spotify: {e}')

            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(2)
                continue
            finally:
                lights.stop_pulsing()
                lights.lights_idle()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()