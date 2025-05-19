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
import threading
import subprocess


# Pre-initialize models and clients
vosk.SetLogLevel(-1)  # Optional: reduce log output
vosk_model = vosk.Model("../../models/vosk-model-small-en-us-0.15")
recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
audio_queue = queue.Queue()

load_dotenv("../../.env")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

def play_wait_sound():
    os.system("mpg321 -q ../../audio/generating.mp3 &")

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
    wait_thread = threading.Thread(target=play_wait_sound)
    wait_thread.start()
    
    transcription_parts = []
    audio_data = bytearray()
    while not audio_queue.empty():
        data = audio_queue.get()
        audio_data.extend(data)
        if len(audio_data) >= 32000:
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
    
    return transcription, time.time() - start_time

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

def text_to_speech(message):
    if not message:
        return 0
    
    start_time = time.time()
    clean_message = re.sub(r"[_*~]", "", message)
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as f:
            tts = gTTS(text=clean_message, lang='en', slow=False)
            tts.save(f.name)
            stop_time = time.time()
            os.system(f"mpg321 -q {f.name}")
    except Exception as e:
        print(f"TTS Error: {e}")  # This will still show!
        return 0
    
    return stop_time - start_time

if __name__ == "__main__":
    try:
        while True:
            start_total_stt = time.time()
            transcription, stt_time = record_and_transcribe()
            total_stt = time.time() - start_total_stt
            
            if transcription:
                ai_start = time.time()
                ai_response = ai_call(transcription)
                ai_time = time.time() - ai_start
                
                tts_start = time.time()
                tts_time = text_to_speech(ai_response)
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