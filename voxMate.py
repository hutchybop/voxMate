import sounddevice as sd
import queue
import vosk
import json
import re
from gtts import gTTS
import os
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import time


# Initialize models
vosk_model = vosk.Model("../../models/vosk-model-small-en-us-0.15")
recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

def record_and_transcribe():
    print("\nPress Enter to start recording...")
    input()
    print("Recording... Press Enter again to stop.")
    
    with sd.RawInputStream(samplerate=16000, blocksize=8000,
                         dtype='int16', channels=1, callback=audio_callback):
        input()  # Wait for Enter to stop
    
    start_stt = time.time()
    # Process all audio data
    transcription = ""
    while not audio_queue.empty():
        data = audio_queue.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                transcription += text + " "
    
    final_result = json.loads(recognizer.FinalResult())
    final_text = final_result.get("text", "")
    print(f"You asked: {final_text}")
    if final_text:
        transcription += final_text
    
    stop_stt = time.time()
    total_stt = stop_stt - start_stt
    
    return transcription.strip(), total_stt

def ai_api(prompt):
    load_dotenv("../../.env")
    
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    response = client.chat.completions.create(
        model="mistral-saba-24b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Respond with only the answer to the question, without repeating the question or adding extra information."},
            {"role": "user", "content": f"Answer this question briefly and clearly: {prompt}"}
        ]
    )
    
    message = response.choices[0].message.content
    print(f"The answer is: {message}")
    return re.sub(r"<think>.*?</think>", "", message, flags=re.DOTALL).strip()

def text_to_speech(message):

    start_tts = time.time()

    clean_message = re.sub(r"[_*~]", "", message)
    tts = gTTS(text=clean_message, lang='en')
    
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        temp_path = f.name
        tts.save(temp_path)

    stop_tts = time.time()

    try:
        os.system(f"mpg321 -q {temp_path}")
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass
        
    total_tts = stop_tts - start_tts

    return total_tts

if __name__ == "__main__":
    try:
        while True:
            start_rec_trans = time.time()
            transcription, total_stt = record_and_transcribe()
            finish_rec_trans = time.time()
            if transcription:
                start_ai = time.time()
                ai_response = ai_api(transcription)
                finish_ai = time.time()
                start_tts_pb = time.time()
                total_tts = text_to_speech(ai_response)
                finish_tts_pb = time.time()
            

            print(f"stt time: {total_stt:.2f} seconds")
            print(f"Rec and Trans time: {finish_rec_trans - start_rec_trans:.2f} seconds")
            print(f"AI response time: {finish_ai - start_ai:.2f} seconds")
            print(f"tts time: {total_tts:.2f} seconds")
            print(f"tts and playback time: {finish_tts_pb - start_tts_pb:.2f} seconds")


            print("\nPress Enter to start again or Ctrl+C to quit")
            input()
    except KeyboardInterrupt:
        print("\nExiting smart speaker...")