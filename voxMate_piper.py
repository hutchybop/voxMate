# Need to install piper locally
# Instructions at: https://github.com/rhasspy/piper
# Slow on RPi4

import sounddevice as sd
import queue
import vosk
import sys
import json
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

def ai_api_stream(prompt):

    load_dotenv("../../.env")
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    stream = client.chat.completions.create(
        model="mistral-saba-24b",
        messages=[
            {"role": "system", "content": "Short, concise, speaker-only replies."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    buffer = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            buffer += token
            if token.endswith(('.', '!', '?')):  # speak sentence by sentence
                yield buffer.strip()
                buffer = ""
    if buffer:
        yield buffer.strip()


def speak_piper(text):
    process = subprocess.Popen(
        ['piper', '--model', '../../models/voices/en_GB-alba-medium.onnx', '--output-raw'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    process.stdin.write(text.encode('utf-8'))
    process.stdin.close()

    # Play audio with aplay or ffplay or stream directly to a player
    subprocess.run(['aplay', '-f', 'S16_LE', '-r', '22050'], input=process.stdout.read())


if __name__ == "__main__":
    import select
    result = record_and_transcribe()
    for sentence in ai_api_stream(result):
        print(f">> {sentence}")
        speak_piper(sentence)