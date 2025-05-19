import os
import sounddevice as sd
import queue
import vosk
import json
import re
from gtts import gTTS
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import time
import subprocess


# Pre-initialize models and clients
vosk.SetLogLevel(-1)  # Optional: reduce log output
vosk_model = vosk.Model("../../models/vosk-model-en-us-0.22")
recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
audio_queue = queue.Queue()
audio_buffer_size = 64000

load_dotenv("../../.env")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

def start_looping_sound():
    return subprocess.Popen(
        ["mpg321", "-q", "--loop", "-1", "../../audio/generating.mp3"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def stop_looping_sound(process):
    if process and process.poll() is None:
        process.terminate()

def audio_callback(indata, frames, time, status):
    if status and status.input_overflow:
        print("Input overflow: increase blocksize")
    audio_queue.put(bytes(indata))

def record_and_transcribe():
    print("\nPress Enter to start recording...")
    input()
    print("Recording... Press Enter again to stop.")
    
    while not audio_queue.empty():
        audio_queue.get()
    
    # Only suppresses warning during this block
    with sd.RawInputStream(samplerate=16000, blocksize=16000, dtype='int16', channels=1, callback=audio_callback):
        input()

    start_time = time.time()
    sound_process = start_looping_sound()
    
    transcription_parts = []
    audio_data = bytearray()
    while not audio_queue.empty():
        data = audio_queue.get()
        audio_data.extend(data)
        if len(audio_data) >= audio_buffer_size:
            if recognizer.AcceptWaveform(bytes(audio_data)):
                result = json.loads(recognizer.Result())
                if text := result.get("text", ""):
                    transcription_parts.append(text)
            audio_data = bytearray()
    
    if audio_data:
        if recognizer.AcceptWaveform(bytes(audio_data)):
            result = json.loads(recognizer.Result())
            if text := result.get("text", ""):
                transcription_parts.append(text)
    
    final_result = json.loads(recognizer.FinalResult())
    if final_text := final_result.get("text", ""):
        transcription_parts.append(final_text)
    
    transcription = " ".join(transcription_parts).strip()
    if transcription:
        print(f"You asked: {transcription}")
    
    return transcription, time.time() - start_time, sound_process

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
            os.system(f"mpg321 -q {f.name}")
    except Exception as e:
        print(f"TTS Error: {e}")  # This will still show!
        return 0
    
    return stop_time - start_time

if __name__ == "__main__":
    try:
        while True:
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
    except KeyboardInterrupt:
        print("\nExiting smart speaker...")