# Required python imports
import subprocess
import time
import tempfile
import os
import wave
import signal
import numpy as np
import sounddevice as sd
from typing import Optional

# Required local imports
from utils.logging import logger
import config.constrants as contrants
import config.settings as settings
from utils.alsa_suppress import suppress_alsa_errors

suppress_alsa_errors()

class AudioProcessor:
    """Handles all audio operations with configurable noise reduction"""
    @staticmethod
    def start_looping_sound() -> subprocess.Popen:
        try:
            return subprocess.Popen(
                ["mpg123", "--stereo", "-q", "--loop", "-1", "-o", "pulse", contrants.GENERATING_SOUND],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.PIPE   # Prevents hanging on terminate
            )
        except FileNotFoundError:
            logger.error("mpg123 not found. Please install mpg123 for audio playback.")
            raise

    @staticmethod
    def stop_looping_sound(process: Optional[subprocess.Popen]) -> None:
        """Stop the background looping sound with mpg123-specific enhancements"""
        if process and process.poll() is None:
            try:
                # 1. Try normal termination
                process.terminate()
                process.wait(timeout=1)
                # 2. Check if mpg123 is still running
                if process.poll() is None:  # Still running
                    # Get the entire process group
                    pgid = os.getpgid(process.pid)
                    # Kill the whole group
                    os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Process already dead
            except subprocess.TimeoutExpired:
                process.kill()  # Fallback
            except Exception as e:
                logger.error(f"Error stopping sound: {e}")
                # Last resort - system level kill
                os.system(f"pkill -9 -f 'mpg123.*{process.args[-1]}'")

    @staticmethod
    def play_sound(file_path: str) -> None:
        """Play sound with explicit stereo output"""
        try:
            result = subprocess.run(
                ["mpg123", "--stereo", "-q", "-o", "pulse", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,  # Capture stderr for debugging
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Error playing sound {file_path}: {e.stderr.decode().strip()}")
            # Fallback to non-stereo mode if needed
            try:
                subprocess.run(
                    ["mpg123", "-q", "-o", "pulse", file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
            except subprocess.CalledProcessError as fallback_e:
                logger.error(f"Fallback playback failed: {fallback_e}")

    @staticmethod
    def record_audio_to_file() -> str:
        """Record audio until silence is detected and save to temporary WAV file"""
        silence_start = None
        audio_data = []
        consecutive_silent_chunks = 0
        
        def callback(indata, frames, time_info, status):
            nonlocal silence_start, consecutive_silent_chunks
            if status and status.input_overflow:
                logger.warning("Input overflow in audio stream detected")
            
            chunk = indata.copy()
            volume = np.linalg.norm(chunk)

            # Shows volume in terminal while mic is in use if set to true
            if settings.VOLUME_DISPLAY:
                print(f"Mic Volume detected: {volume}")

            
            if settings.NOISE_REDUCTION_ENABLED:
                if volume > settings.SILENCE_THRESHOLD:
                    audio_data.append(chunk)
                    consecutive_silent_chunks = 0
                elif audio_data:
                    consecutive_silent_chunks += 1
                    if consecutive_silent_chunks > int(settings.SILENCE_DURATION * contrants.SAMPLE_RATE / contrants.BLOCKSIZE):
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

            # Save to temp WAV file
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            with wave.open(temp_audio.name, 'wb') as wf:
                wf.setnchannels(contrants.CHANNELS)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(contrants.SAMPLE_RATE)
                for chunk in audio_data:
                    wf.writeframes(chunk.tobytes())
            
            logger.debug(f"Recorded {len(audio_data)} chunks (Noise reduction: {'ON' if settings.NOISE_REDUCTION_ENABLED else 'OFF'})")
            return temp_audio.name
            
        except Exception as e:
            logger.error(f"Error: {e}")
            os.unlink(temp_audio.name)
            raise
