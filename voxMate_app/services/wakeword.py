# Required python imports
from contextlib import contextmanager
from typing import Tuple, Generator
import pyaudio
import pvporcupine
import struct

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
    while True:
        try:
            # Stops Spotify if playing to use the speaker
            spotify_player = SpotifyPlayer()
            spotify_player.stop_playback()
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            if porcupine.process(pcm) >= 0:
                logger.info("Wake word detected! Ask your question...")
                # wake word stream must be closed BEFORE recording speech
                AudioProcessor.play_sound(constrants.GREETING_SOUND)
                break
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            raise