from dataclasses import dataclass, field


@dataclass
class User:
    _id: str
    email: str
    password: str
    appSettings_id: str = field(default_factory=lambda: "default")