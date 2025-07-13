# Required python imports
from contextlib import contextmanager
from typing import Tuple, Generator
import pyaudio
import pvporcupine
import struct
import time

# Required local imports
import config.constrants as constrants
from utils.logging import logger
from services.audio import AudioProcessor
from services.spotify_app import SpotifyPlayer


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
            keyword_paths=[constrants.KEYWORD_PATH],
            sensitivities=[0.7]
        )

        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=constrants.CHANNELS,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=1,
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
    logger.info(f"Listening for wake word... (say '{constrants.WAKE_WORD}')")
    # Initialize SpotifyPlayer once outside the loop
    spotify_player = SpotifyPlayer()
    max_pause_attempts = 3
    spotify_stopped = False  # Track if we've already stopped playback
    while True:
        try:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            if porcupine.process(pcm) >= 0:
                logger.info("Wake word detected! Ask your question...")
                # Stop Spotify only if we haven't already done so
                if not spotify_stopped:
                    for attempt in range(max_pause_attempts):
                        if spotify_player.stop_playback():
                            spotify_stopped = True
                            logger.debug("Wake word detected, Spotify paused successfully")
                            break
                        elif attempt == max_pause_attempts - 1:
                            logger.error("Critical: Failed to detect wake word, failed to pause Spotify after retries")
                            return  # Exit wake word detection entirely
                        time.sleep(0.1)
                # Wake word stream must be closed BEFORE recording speech
                AudioProcessor.play_sound(constrants.GREETING_SOUND)
                break
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            raise