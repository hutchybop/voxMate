import sounddevice as sd
import wavio as wv
import vosk
import numpy as np
from huggingface_hub import InferenceClient
import re
import json
import time
from gtts import gTTS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../../.env")


def rec():
    freq = 16000
    duration = 5

    print("Enter 'r' to start your question...")

    while True:
        start = input().strip().lower()
        if start == 'r':
            break
    
    print("Recording question, press 's' to finish...")
    recordings = []

    while True:
        recording = sd.rec(int(duration * freq), samplerate=freq, channels=1)
        sd.wait()
        recordings.append(recording)

        finish = input().strip().lower()
        if finish == 's':
            time.sleep(1)
            break
    
    full_recording = np.concatenate(recordings, axis=0)
    audio_int16 = np.int16(full_recording * 32767)
    audio_bytes = audio_int16.tobytes()
    return audio_bytes


def speech_to_text(audio_bytes):
    model = vosk.Model("/home/hutch/smartSpeaker/vosk-model-small-en-us-0.15")
    recognizer = vosk.KaldiRecognizer(model, 16000)

    chunk_size = 4000
    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i:i+chunk_size]
        recognizer.AcceptWaveform(chunk)

    result_json = recognizer.FinalResult()
    result_dict = json.loads(result_json)
    recognized_text = result_dict.get("text", "")

    print(f"""
        Your question has been converted to text, here is what I think you said:
        {recognized_text}
        This will now be sent to AI to get your answer.
        """)
    
    return recognized_text


def ai_api(result):
    client = InferenceClient(
        provider="together",
        api_key=os.getenv("HUGGINGFACE_HUB"),
    )
    model = "deepseek-ai/DeepSeek-R1"

    print('Getting your answer from: ' + model + ' Please stand by...')

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Please provide a short concise answer to this question: " + result
            }
        ],
    )
    message = completion.choices[0].message.content

    # Remove <think>...</think> content if present
    message = re.sub(r"<think>.*?</think>", "", message, flags=re.DOTALL).strip()
    print(message)
    return message


def text_to_speech(message):
    tts = gTTS(text=message, lang='en')
    tts.save("output.mp3")
    os.system("mpg321 output.mp3")


if __name__ == "__main__":
    audio_bytes = rec()
    result = speech_to_text(audio_bytes)
    message = ai_api(result)
    text_to_speech(message)