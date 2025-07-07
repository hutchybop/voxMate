# Required python imports
from openai import OpenAI
import os
import time
import re
import tempfile
import json
from gtts import gTTS
import subprocess
from typing import Optional, Tuple


# Required local imports
from utils.logging import logger
from services.audio import AudioProcessor
import config.settings as settings
from config.ai_prompt import ai_prompt
from services.spotify_app import handle_spotify_play


class AIService:
    """Handles all AI-related operations"""
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.access_key = os.getenv("PORCUPINE_API_KEY")

        if not self.access_key:
            logger.error("Porcupine API key not found in environment variables")
            raise ValueError("Missing API key")
        
    def transcribe_audio(self, audio_path: str) -> Tuple[str, float, subprocess.Popen]:
        """Transcribe audio using Whisper API"""
        sound_process = AudioProcessor.start_looping_sound()
        start_time = time.time()

        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=settings.STT_MODEL,
                    file=audio_file,
                    language="en",
                    response_format="text"
                )

            if transcript:
                logger.info(f"Transcription: {transcript.strip()}")
            return transcript.strip(), time.time() - start_time, sound_process
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            AudioProcessor.stop_looping_sound(sound_process)
            raise
        finally:
            try:
                os.unlink(audio_path)
            except Exception as e:
                logger.error(f"Error deleting temp audio file: {e}")

    def generate_response(self, prompt: str) -> str:
        """Generate AI response using chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=ai_prompt(prompt),
                max_tokens=100,
                temperature=0.7
            )
            message = response.choices[0].message.content
            # Remove any special formatting tags
            cleaned = re.sub(r"<think>.*?</think>", "", message, flags=re.DOTALL)
            cleaned = re.sub(r"^```(?:json)?\s*|```$", "", cleaned, flags=re.MULTILINE).strip()
            logger.info(f"AI Response: {cleaned}")
            try:
                parsed = json.loads(cleaned)
                response_text = parsed.get("response")
                if parsed.get("action") == "spotify_play":
                    # play_spotify = handle_spotify_play(parsed.get("params", ""))
                    play_spotify = {"params": parsed.get("params", "")}
                else:
                    play_spotify = None
                return response_text, play_spotify
            except json.JSONDecodeError:
                pass  # Fall through to return plain text
            return cleaned
        except Exception as e:
            logger.error(f"AI API Error: {e}")
            return "Sorry, I encountered an error processing your request."

    def text_to_speech(self, message: str, sound_process: Optional[subprocess.Popen]) -> float:
        """Convert text to speech and play it"""
        if not message:
            return 0
        
        start_time = time.time()

        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as f:
                # Clean special characters that might cause TTS issues
                clean_text = re.sub(r"[_*~]", "", message)
                gTTS(text=clean_text, lang='en').save(f.name)
                AudioProcessor.stop_looping_sound(sound_process)
                stop_time = time.time()
                AudioProcessor.play_sound(f.name)
                return stop_time - start_time
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return 0