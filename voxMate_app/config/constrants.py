# Required python imports
import os
from pathlib import Path


# Other default variables
SAMPLE_RATE = 16000
CHANNELS = 2
DTYPE = 'int16'
BLOCKSIZE = 16000
WAKE_WORD = 'Hey VoxMate'

# Paths
# Get absolute path to be safe
KEYWORD_PATH = Path(__file__).resolve().parent.parent / "models" / os.getenv("PORCUPINE_KEYWORD_FILE_NAME")
GENERATING_SOUND = Path(__file__).resolve().parent.parent / "audio" / "generating.mp3"
GREETING_SOUND = Path(__file__).resolve().parent.parent / "audio" / "greeting.mp3"
MONGODB_WARNING_SOUND = Path(__file__).resolve().parent.parent / "audio" / "warning_mongodb.mp3"
CRITICAL_ENV_VAR_SOUND = Path(__file__).resolve().parent.parent / "audio" / "critical_env_var.mp3"