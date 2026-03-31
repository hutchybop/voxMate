from gtts import gTTS
import subprocess
import re
import time


def text_to_speech(message):

    start_total = time.time()

    clean_message = re.sub(r"\*\*(.*?)\*\*", r"\1", message)
    clean_message = re.sub(r"[_*~]", "", clean_message)

    tts = gTTS(text=message, lang='en')

    tts.save("py_test.mp3")

    stop_total = time.time()

    subprocess.run([
        "mpg321", "-q", "py_test.mp3"  # -q for quiet mode
    ])

    

    print(f"Total Time to create audio: {stop_total - start_total:.2f} seconds")


while True:

    quest = input("What you wnat to say? Type 'stop' to finish: ")

    if quest == 'stop':
        break
    
    text_to_speech(quest)

