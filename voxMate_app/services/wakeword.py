# Required python imports
from contextlib import contextmanager
from typing import Tuple, Generator
import pyaudio
import numpy as np
import time
import os
from openwakeword import Model as oww_Model

# Required local imports
import config.constraints as constraints
from utils.logging import logger
from services.audio import AudioProcessor
from utils.state import app_state
from actions.dispatcher import handle_action
from utils.mic_lights import MicLights

@contextmanager
def audio_wake_stream() -> Generator[Tuple[oww_Model, pyaudio.Stream], None, None]:
    """Context manager for OpenWakeWord wake word detection"""
    pa = None
    oww_model = None
    stream = None
    try:
        pa = pyaudio.PyAudio()
        
        # Initialize OpenWakeWord model
        oww_model = oww_Model(wakeword_models=[constraints.KEYWORD_PATH])

        try:
            stream = pa.open(
                rate=constraints.SAMPLE_RATE,
                channels=constraints.CHANNELS,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=constraints.FRAME_LENGTH,
            )
        except Exception as e:
            logger.error(f"Failed to open audio stream: {e}")
            raise
    
        yield oww_model, stream

    except Exception as e:
        logger.error(f"Error initializing: {e}")
        raise
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        if pa:
            pa.terminate()


def wake_word_detection(oww_model: oww_Model, stream: pyaudio.Stream, mic_lights: MicLights) -> None:
    """Listen for wake word and respond when detected"""
    logger.info(f"Listening for wake word... (say '{constraints.WAKE_WORD}')")
    while True:
        try:
            pcm = stream.read(constraints.FRAME_LENGTH, exception_on_overflow=False)
            
            # Convert to numpy array and handle stereo to mono
            audio_data = np.frombuffer(pcm, dtype=np.int16)
            if constraints.CHANNELS == 2:
                # Convert stereo to mono by averaging
                audio_data = audio_data.reshape(-1, 2).mean(axis=1).astype(np.int16)

            predictions = oww_model.predict(audio_data)

            score = predictions.get(constraints.WAKE_WORD, 0.0)

            # Check if your wake word is detected (threshold typically 0.5-0.8)
            if score > 0.7:  # Adjust threshold as needed
                mic_lights.lights_wake_word()
                logger.info("Wake word detected! Ask your question...")

                if app_state.is_spotify_playing():
                    success, _ = handle_action({"action": "spotify_stop"})
                    if success:
                        app_state.set_state("spotify", "paused")
                        logger.info("Spotify paused successfully")
                    else:
                        logger.warning("Failed to pause Spotify")
                
                time.sleep(0.5)
                AudioProcessor.play_sound(constraints.GREETING_SOUND)
                break
        
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
