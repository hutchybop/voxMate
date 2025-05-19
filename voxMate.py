import os
import sounddevice as sd
import queue
import re
from gtts import gTTS
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import time
import subprocess
import signal
import atexit
import sys
import pvporcupine
import pyaudio
import struct
from ctypes import *


# ALSA error handler
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
try:
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass  # Skip if not on Linux

# Audio Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'
BLOCKSIZE = 16000
audio_queue = queue.Queue()
sound_process = None

cleanup_done = False

# Initialize OpenAI client
load_dotenv("../../.env")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

access_key = os.getenv("PORCUPINE_API_KEY")

# Initialize Porcupine
porcupine = pvporcupine.create(access_key=access_key, keyword_paths=['../../models/porcupine_keywords/hey-bop_en_raspberry-pi_v3_0_0.ppn'])

# Initialize PyAudio with suppressed errors
with open(os.devnull, 'w') as devnull:
    old_stderr = os.dup(sys.stderr.fileno())
    os.dup2(devnull.fileno(), sys.stderr.fileno())
    
    pa = pyaudio.PyAudio()
    
    os.dup2(old_stderr, sys.stderr.fileno())

stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length,
)


def cleanup():
    global sound_process, cleanup_done
    if cleanup_done:
        return
    cleanup_done = True

    stop_looping_sound(sound_process)

    try:
        if stream and stream.is_active():
            stream.stop_stream()
        stream.close()
    except Exception as e:
        print(f"Stream cleanup error: {e}")

    try:
        if pa:
            pa.terminate()
    except Exception as e:
        print(f"PyAudio cleanup error: {e}")

    try:
        if porcupine:
            porcupine.delete()
    except Exception as e:
        print(f"Porcupine cleanup error: {e}")

    print("Cleaned up and exiting.")


atexit.register(cleanup)
signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))
signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))  # Ctrl+C


def start_looping_sound():
    return subprocess.Popen(
        ["mpg321", "-q", "--loop", "-1", "../../audio/generating.mp3"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def stop_looping_sound(process):
    if process and process.poll() is None:
        process.terminate()

def audio_callback(indata, frames, time, status):
    if status and status.input_overflow:
        print("Input overflow: increase blocksize")
    audio_queue.put(bytes(indata))

def wake_word():
    print("Listening for wake word... (say 'Hey Bop')")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                subprocess.run(
                    ["mpg321", "-q", "../../audio/greeting.mp3"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                break

    except KeyboardInterrupt:
        print("Stopping...")


def record_audio_to_file():
    # Record audio to temporary WAV file for Whisper
    print("\nRecording, press enter to stop...")
    
    # Create temp file
    temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    
    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE,
                             dtype=DTYPE, channels=CHANNELS, callback=audio_callback):
            input()
        
        # Convert raw audio to WAV format
        import wave
        with wave.open(temp_audio.name, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit = 2 bytes
            wf.setframerate(SAMPLE_RATE)
            while not audio_queue.empty():
                wf.writeframes(audio_queue.get())
        
        return temp_audio.name
    
    except Exception as e:
        temp_audio.close()
        os.unlink(temp_audio.name)
        raise e

def transcribe_with_whisper(audio_path):
    """Use Whisper for transcription"""
    start_time = time.time()
    sound_process = start_looping_sound()
    
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=audio_file,
                language="en",
                response_format="text"
            )
        return transcript.strip(), time.time() - start_time, sound_process
    finally:
        os.unlink(audio_path)  # Clean up temp file

def record_and_transcribe():
    audio_file = record_audio_to_file()
    transcription, stt_time, sound_process = transcribe_with_whisper(audio_file)
    if transcription:
        print(f"You asked: {transcription}")
    return transcription, stt_time, sound_process

def ai_call(prompt):
    try:
        response = client.chat.completions.create(
            model="mistral-saba-24b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Answer briefly: {prompt}"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        message = response.choices[0].message.content
        print(f"The answer is: {message}")
        return re.sub(r"<think>.*?</think>", "", message, flags=re.DOTALL).strip()
    except Exception as e:
        print(f"API Error: {e}")  # This will still show!
        return "Sorry, I encountered an error."

def text_to_speech(message, sound_process):
    if not message:
        return 0

    start_time = time.time()
    clean_message = re.sub(r"[_*~]", "", message)
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as f:
            tts = gTTS(text=clean_message, lang='en', slow=False)
            tts.save(f.name)
            stop_time = time.time()
            stop_looping_sound(sound_process)
            subprocess.run(
                ["mpg321", "-q", f.name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
    except Exception as e:
        print(f"TTS Error: {e}")  # This will still show!
        return 0
    
    return stop_time - start_time

if __name__ == "__main__":
    try:
        while True:
            wake_word()
            start_total_stt = time.time()
            transcription, stt_time, sound_process = record_and_transcribe()
            total_stt = time.time() - start_total_stt
            
            if transcription:
                ai_start = time.time()
                ai_response = ai_call(transcription)
                ai_time = time.time() - ai_start
                
                tts_start = time.time()
                tts_time = text_to_speech(ai_response, sound_process)
                total_tts_time = time.time() - tts_start
                
                print(f"\nPerformance Metrics:")
                print(f"- STT Processing: {stt_time:.2f}s")
                print(f"- STT & Playback: {total_stt:.2f}")
                print(f"- AI Response: {ai_time:.2f}s")
                print(f"- TTS & Playback: {total_tts_time:.2f}s")
                print(f"- TTS Generation: {tts_time:.2f}s")
            
            print("\nPress Enter to start again or Ctrl+C to quit")
            input()

    except Exception as e:
        print("\nExiting smart speaker...")
    finally:
        cleanup()
