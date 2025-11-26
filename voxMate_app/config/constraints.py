# Required python imports
import os
from pathlib import Path


# Other default variables
SAMPLE_RATE = 16000
FRAME_LENGTH = 512
CHANNELS = 2
DTYPE = 'int16'
BLOCKSIZE = 16000
# WAKE_WORD = 'Hey VoxMate'
WAKE_WORD = 'hey_jarvis'

# Paths
# Get absolute path to be safe
KEYWORD_PATH = Path(__file__).resolve().parent.parent / "models" / os.getenv("OPENWAKEWORD_KEYWORD_FILE_NAME")
# KEYWORD_PATH = Path(__file__).resolve().parent.parent / "models" / os.getenv("PORCUPINE_KEYWORD_FILE_NAME")
GENERATING_SOUND = Path(__file__).resolve().parent.parent / "audio" / "generating.mp3"
GREETING_SOUND = Path(__file__).resolve().parent.parent / "audio" / "greeting.mp3"
MONGODB_WARNING_SOUND = Path(__file__).resolve().parent.parent / "audio" / "warning_mongodb.mp3"
CRITICAL_ENV_VAR_SOUND = Path(__file__).resolve().parent.parent / "audio" / "critical_env_var.mp3"

# Spotify configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_CALLBACK_URL')
SCOPES = " ".join([
    "user-read-currently-playing",
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-library-read",
    "playlist-read-private"
])
SPOTIFY_DEVICE_ID = "b16c033229c6e42b50fcc84989e90f4fc0be26c0"      # Pi
# SPOTIFY_DEVICE_ID = "775086b5c0c806bad6dbb0652ba4d7003b7e0b32"      # mac