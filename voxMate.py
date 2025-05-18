# recording -> vosk -> groq -> gtts

import sounddevice as sd
import queue
import vosk
import sys
import json
import re
from gtts import gTTS
import os
from openai import OpenAI
from dotenv import load_dotenv
import subprocess
import time

q = queue.Queue()

voskModel = vosk.Model("../../models/vosk-model-small-en-us-0.15")
recognizer = vosk.KaldiRecognizer(voskModel, 16000)
# aiModel = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# aiModel = "deepseek-ai/DeepSeek-R1"
aiModel = "mistral-saba-24b"

start_total = time.time()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def record_and_transcribe():
    print("Press Enter to start recording, and Enter again to stop...")
    input()

    print("Recording... Press Enter again to stop.")
    transcription = ""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                input()
                break

            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                transcription += result.get("text", "") + " "
            else:
                partial = json.loads(recognizer.PartialResult())

        final_result = json.loads(recognizer.FinalResult())
        transcription += final_result.get("text", "")

    print(f"\nRecognized: {transcription.strip()}")
    return transcription.strip()

def ai_api(prompt):

    load_dotenv("../../.env")

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model=aiModel,
        messages=[
            {"role": "system", "content": "You are to give short concise answers to questions, which will only be played back on a speraker."},
            {"role": "user", "content": prompt}
        ]
    )
    message = response.choices[0].message.content
    message = re.sub(r"<think>.*?</think>", "", message, flags=re.DOTALL).strip()
    print(message)
    return message


def text_to_speech(message):
    clean_message = re.sub(r"\*\*(.*?)\*\*", r"\1", message)
    clean_message = re.sub(r"[_*`~]", "", clean_message)

    tts = gTTS(text=clean_message, lang='en')
    tts.save("output.mp3")
    subprocess.run([
        "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "output.mp3"
    ])
    os.remove("output.mp3")
    # os.system("mpg321 output.mp3")


if __name__ == "__main__":
    import select

    
    result = record_and_transcribe()


    start_processing = time.time()
    message = ai_api(result)
    end_processing = time.time()

    start_tts = time.time()
    text_to_speech(message)
    end_tts = time.time()

    end_total = time.time()

    # --- Print timing results ---
    # print(f"Speech Recognition Time: {end_sr - start_sr:.2f} seconds")
    print(f"AI Response time:         {end_processing - start_processing:.2f} seconds")
    print(f"Text-to-Speech Time:     {end_tts - start_tts:.2f} seconds")
    print(f"Total Time (not including STT):              {end_total - start_total:.2f} seconds")