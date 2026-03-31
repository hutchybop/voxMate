import pyttsx3

def text_to_speech(message):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Adjust speed here
    engine.say(message)
    engine.runAndWait()

text_to_speech('Hi, this is a test. hopefully you can hear everything I say.')