# Importing required libraries
import sounddevice as sd
import wavio as wv

# Setting the audio frequency
freq = 16000

# Setting the record duration (seconds)
duration = 5

# Setting the parameters of the recorder.
# channels=1 is mono and =2 is sterio
# Will create a NumPy output, which will be converted below
recording = sd.rec(int(duration * freq), samplerate=freq, channels=1)
sd.wait()

# Convert the NumPy array to audio file
wv.write("../../audio/recording.wav", recording, freq, sampwidth=2)
