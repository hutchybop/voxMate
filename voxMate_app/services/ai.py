# Required python imports
from openai import OpenAI
import os
import time
import re
import tempfile
import json
from gtts import gTTS
import subprocess
from typing import Tuple, Optional


# Required local imports
from utils.logging import logger
from services.audio import AudioProcessor
import config.settings as settings
from config.ai_prompt import ai_prompt
import config.constraints as constraints


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
        AudioProcessor.play_sound(constraints.GENERATING_SOUND)
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
            return transcript.strip(), time.time() - start_time
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            try:
                os.unlink(audio_path)
            except Exception as e:
                logger.error(f"Error deleting temp audio file: {e}")


    def generate_response(self, prompt: str) -> Tuple[str, Optional[dict]]:
        """Generate AI response using chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=ai_prompt(prompt),
                max_tokens=200,
                temperature=0.3,
            )
            message = response.choices[0].message.content

            # Remove any special formatting tags
            cleaned = re.sub(r"<think>.*?</think>", "", message, flags=re.DOTALL)
            cleaned = re.sub(r"```(?:json)?\n(.*?)```", r"\1", cleaned, flags=re.DOTALL).strip()

            try:
                parsed = json.loads(cleaned)
                if not isinstance(parsed, dict):
                    logger.warning(f"Parsed response is not a JSON object: {cleaned}")
                    logger.info(f"Original ai response: {message}")
                    return cleaned, None
                logger.info(f"AI Response: {parsed}")
                response_text = parsed.get("response") or message
                if parsed.get("action"):
                    return response_text, parsed
                else:
                    return response_text, None

            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed: {e}")
                return cleaned, None

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "Sorry, I encountered an error processing your request.", None


    def text_to_speech(self, message: str) -> float:
        """Convert text to speech and play it"""
        if not message:
            return 0
        
        start_time = time.time()

        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as f:
                # Clean special characters that might cause TTS issues
                clean_text = re.sub(r"[_*~]", "", message)
                gTTS(text=clean_text, lang='en').save(f.name)
                stop_time = time.time()
                AudioProcessor.play_sound(f.name)
                return stop_time - start_time
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return 0