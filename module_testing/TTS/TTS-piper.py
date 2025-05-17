# Need to install piper locally
# Instructions at: https://github.com/rhasspy/piper
# Slow on RPi4

import subprocess
import re
import time


def text_to_speech(message):

    start_total = time.time()

    clean_message = re.sub(r"\*\*(.*?)\*\*", r"\1", message)
    clean_message = re.sub(r"[_*~]", "", clean_message)


    # Run piper to synthesize the speech
    output_speech = subprocess.run(
        [
            "piper",
            "--model", "/home/hutch/smartSpeaker/voices/en_GB-alba-medium.onnx",
            "--output_file", "py_test.wav"
        ],     
        input=clean_message,
        text=True,
        check=True
    )

    stop_total = time.time()

    subprocess.run([
        "aplay", "py_test.wav" 
    ])



    print(f"Total Time: {stop_total - start_total:.2f} seconds")


while True:

    quest = input("What you wnat to say? Type 'stop' to finish: ")

    if quest == 'stop':
        break
    
    text_to_speech(quest)