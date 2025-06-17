from dataclasses import dataclass, field


@dataclass
class User:
    _id: str
    email: str
    password: str
    appSettings_id: str = field(default_factory=lambda: "default")

@dataclass
class AppSettings:
    _id: str
    email: str
    silence_threshold: int = 14200
    silence_duration: int = 1
    noise_reduction: bool = True
    stt_model: str = 'whisper-large-v3-turbo'
    ai_model: str = 'mistral-saba-24b'

