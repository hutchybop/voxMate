# Required python imports
from openai import OpenAI
import os
import re
import tempfile
import json
from gtts import gTTS
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
        
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using Whisper API"""
        AudioProcessor.play_sound(constraints.GENERATING_SOUND)
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
            # None return is delt with in main.py
            return transcript.strip()
        except Exception as e:
            logger.error(f"Error: {e}")
            # This function is critical, rase here so main.py handles the error in the except block
            raise
        finally:
            try:
                os.unlink(audio_path)
            except Exception as e:
                # No raise as deleting the temp file with no stop the app
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


    def text_to_speech(self, message: str) -> None:
        """Convert text to speech and play it"""
        if not message:
            logger.warning("No message provided for TTS")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as f:
                # Clean special characters that might cause TTS issues
                clean_text = re.sub(r"[_*~]", "", message)
                gTTS(text=clean_text, lang='en').save(f.name)
                AudioProcessor.play_sound(f.name)
                return True
            
        except Exception as e:
            logger.error(f"TTS Error: {e}")