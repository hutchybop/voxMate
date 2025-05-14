from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../../.env")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Path to your audio file
# audio_file_path = "/home/hutch/smartSpeaker/recording1.mp3"
audio_file_path = "../../audio/py_test.mp3"

# Open the audio file in binary mode
with open(audio_file_path, "rb") as audio_file:
    # Transcribe the audio using Groq's Whisper model
    transcript = client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",
        file=audio_file,
        language="en",  # Specify the language code
        response_format="text"  # Options: 'json', 'verbose_json', or 'text'
    )

# Print the transcribed text
print(transcript)
