from dataclasses import dataclass, field


@dataclass
class User:
    _id: str
    email: str
    password: str
    movies: list[str] = field(default_factory=list)