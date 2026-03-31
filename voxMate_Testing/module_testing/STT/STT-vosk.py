import vosk

# load the vosk model
model = vosk.Model("../../models/vosk-model-small-en-us-0.15")

# Initialise the recogniser with the model
recognizer = vosk.KaldiRecognizer(model, 16000)

# define the audio file
audio_file = "../../audio/recording.wav"

# Open the audio file
with open(audio_file, "rb") as audio:
    while True:
        # read the audio file
        data = audio.read(4000)
        if len(data) == 0:
            break
        # Recognize the speech in the chunk
        recognizer.AcceptWaveform(data)

# Get the result
result = recognizer.FinalResult()
print(result)