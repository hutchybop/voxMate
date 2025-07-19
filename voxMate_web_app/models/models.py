# Required python imports
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


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
    MIC_DEVICE_INDEX: Optional[str] = None


@dataclass
class VoxSpotify:
    user_id: str
    token_info: Optional[Dict[str, Any]] = None
    device_id: Optional[str] = None
    last_updated: Optional[datetime] = None
    user_code: Optional[str] = None

