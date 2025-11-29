import subprocess
import time
import tempfile
import os
import wave
import numpy as np
import sounddevice as sd

from utils.logging import logger
import config.constraints as contrants
import config.settings as settings
from utils.alsa_suppress import suppress_alsa_errors

suppress_alsa_errors()


class AudioProcessor:
    """Handles all audio operations with configurable noise reduction"""

    @staticmethod
    def play_sound(file_path: str) -> None:
        """Play sound with explicit stereo output"""
        try:
            subprocess.run(
                ["mpg123", "--stereo", "-q", "-o", "pulse", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,  # Capture stderr for debugging
                check=True,
            )
        except subprocess.CalledProcessError as e:
            # Do not need to raise here as this would not cause a critical error
            logger.error(
                f"Error playing sound {file_path}: {e.stderr.decode().strip()}"
            )
            # Fallback to non-stereo mode if needed
            try:
                subprocess.run(
                    ["mpg123", "-q", "-o", "pulse", file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
            except subprocess.CalledProcessError as fallback_e:
                # Do not need to raise here as this would not cause a critical error
                logger.error(f"Fallback playback failed: {fallback_e}")

    @staticmethod
    def record_audio_to_file() -> str:
        """Record audio until silence is detected and save to temporary WAV file"""
        silence_start = None
        audio_data = []
        consecutive_silent_chunks = 0

        def callback(
            indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags
        ) -> None:
            nonlocal silence_start, consecutive_silent_chunks
            if status and status.input_overflow:
                logger.warning("Input overflow in audio stream detected")

            chunk = indata.copy()
            volume = np.linalg.norm(chunk)

            if settings.VOLUME_DISPLAY:
                print(f"Mic Volume detected: {volume}")

            if settings.NOISE_REDUCTION_ENABLED:
                if volume > settings.SILENCE_THRESHOLD:
                    audio_data.append(chunk)
                    consecutive_silent_chunks = 0
                elif audio_data:
                    consecutive_silent_chunks += 1
                    threshold_chunks = int(
                        settings.SILENCE_DURATION
                        * contrants.SAMPLE_RATE
                        / contrants.BLOCKSIZE
                    )
                    if consecutive_silent_chunks > threshold_chunks:
                        raise sd.CallbackStop()
            else:
                audio_data.append(chunk)
                if volume < settings.SILENCE_THRESHOLD:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > settings.SILENCE_DURATION:
                        raise sd.CallbackStop()
                else:
                    silence_start = None

        try:
            with sd.InputStream(
                samplerate=contrants.SAMPLE_RATE,
                dtype=contrants.DTYPE,
                channels=contrants.CHANNELS,
                callback=callback,
                blocksize=contrants.BLOCKSIZE,
            ) as stream:
                logger.info("Recording... (speak now)")
                while stream.active:
                    time.sleep(0.1)

            temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            with wave.open(temp_audio.name, "wb") as wf:
                wf.setnchannels(contrants.CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(contrants.SAMPLE_RATE)
                for chunk in audio_data:
                    wf.writeframes(chunk.tobytes())

            logger.debug(
                f"Recorded {len(audio_data)} chunks (Noise reduction: "
                f"{'ON' if settings.NOISE_REDUCTION_ENABLED else 'OFF'})"
            )
            return temp_audio.name

        except Exception as e:
            logger.error(f"Error: {e}")
            if "temp_audio" in locals() and os.path.exists(temp_audio.name):
                os.unlink(temp_audio.name)
            # This function is critical, raise here so main.py handles
            # the error in the except block
            raise
