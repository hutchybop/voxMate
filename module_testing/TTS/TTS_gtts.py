from gtts import gTTS
import os

text = "Hello from your Raspberry Pi!"
tts = gTTS(text=text, lang='en')
tts.save("output.mp3")
os.system("mpg321 output.mp3")