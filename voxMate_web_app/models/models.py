from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    email: str
    password: str
    verify: bool
    device_id: str
    user_id: Optional[str] = None
    unverified_user_id: Optional[str] = None
    api_token: Optional[str] = None

@dataclass
class AppSettings:
    user_id: str
    email: str
    silence_threshold: int = 14200
    silence_duration: int = 1
    volume_display: bool = False
    noise_reduction: bool = True
    stt_model: str = 'whisper-large-v3-turbo'
    ai_model: str = 'mistral-saba-24b'

