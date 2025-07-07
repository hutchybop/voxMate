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
            keyword_paths=[constrants.KEYWORD_PATH]
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
    logger.info(f"Listening for wake word... (say '{constrants.WAKE_WORD}')")
    while True:
        try:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            if porcupine.process(pcm) >= 0:
                logger.info("Wake word detected! Ask your question...")
                AudioProcessor.play_sound(constrants.GREETING_SOUND)
                break
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            raise