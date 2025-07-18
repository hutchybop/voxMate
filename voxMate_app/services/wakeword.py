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
from actions.handlers.spotify_app import SpotifyPlayer
from utils.state import app_state
from actions.dispatcher import handle_cmd


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
            input_device_index=0,
            frames_per_buffer=porcupine.frame_length,
        )
        yield porcupine, pa, stream
    except Exception as e:
        logger.error(f"Error initializing: {e}")
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
    while True:
        try:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            # Convert to mono by averaging stereo channels
            samples = struct.unpack_from("h" * porcupine.frame_length * 2, pcm)  # 2 channels
            mono_samples = [(samples[i] + samples[i+1]) // 2 for i in range(0, len(samples), 2)]
            if porcupine.process(mono_samples) >= 0:
                logger.info("Wake word detected! Ask your question...")
                # Stop Spotify only if we haven't already done so
                if app_state.is_spotify_playing():
                    for attempt in range(max_pause_attempts):
                        cmd_response = handle_cmd({"cmd": "spotify_stop"})
                        if cmd_response:
                            app_state.set_state("spotify", "paused")
                            logger.info("Spotify paused successfully")
                            break
                        elif attempt == max_pause_attempts - 1:
                            logger.error("Critical: Failed to detect wake word, failed to pause Spotify after retries")
                            return  # Exit wake word detection entirely
                        time.sleep(0.1)
                AudioProcessor.play_sound(constrants.GREETING_SOUND)
                break
        except Exception as e:
            logger.error(f"Error: {e}")
            raise