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
from actions.dispatcher import handle_action
from utils.mic_lights import MicLights

def main() -> None:
    """Main execution loop"""
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    # Initialize services
    audio = AudioProcessor()
    atexit.register(cleanup)
    mic_lights = MicLights()

    # Check environment variables before proceeding  
    settings.check_environment(audio_player=audio)

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

        # Setting system default volume
        success, message = handle_action({"action": "volume", "level": settings.DEFAULT_VOLUME})
        if not success and message:
            ai_service.text_to_speech(message)
   
        
        while True:
            try:

                print(os.getenv("REMOTE"))

                if os.getenv("REMOTE") == "False":

                    app_state.set_state("status", "waiting")
                    mic_lights.lights_idle()

                    # Wake word phase (PyAudio holds mic)
                    with wakeword.audio_wake_stream(ai_service.access_key) as (porcupine, stream):
                        wakeword.wake_word_detection(porcupine, stream, mic_lights)

                    # Mic now released — record using sounddevice
                    app_state.set_state("status", "processing")
                    mic_lights.lights_listening()

                    audio_file = AudioProcessor.record_audio_to_file()

                    mic_lights.lights_pulsing_processing()

                    transcript = ai_service.transcribe_audio(audio_file)
                
                else: 
                    transcript = input("Enter the user question: ")

                if transcript:
                    # AI response generation
                    try:
                        response_text, parsed = ai_service.generate_response(transcript)
                        if not isinstance(response_text, str):
                            response_text = str(response_text)
                    except Exception as e:
                        logger.error(f"AI processing failed: {e}")
                        response_text = "Sorry, I encountered an error processing your request"
                        parsed = None

                    # Handle the user command and play response
                    try:
                        if parsed is not None and parsed.get("action"):
                            success, message = handle_action(parsed)
                            if not success and message:
                                ai_service.text_to_speech(message)
                            else:
                                ai_service.text_to_speech(response_text)
                        else:
                            ai_service.text_to_speech(response_text)
                    except Exception as e:
                        logger.error(f'Main loop error, processing user command: {e}')

                else:
                    # Fall back if no recording
                    logger.warning("No sound recorded")
                    no_recoding_response = "Nothing heard, sleeping"
                    ai_service.text_to_speech(no_recoding_response)

                try:
                    # Resume Spotify play if paused
                    if app_state.is_spotify_paused():
                        success, message = handle_action({"action": "spotify_play"})
                        if not success and message:
                            ai_service.text_to_speech(message)
                except Exception as e:
                    logger.error(f'Error re-starting Spotify: {e}')

            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(2)
                continue
            finally:
                mic_lights.stop_pulsing()
                mic_lights.lights_idle()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()