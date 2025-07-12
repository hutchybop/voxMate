from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

@dataclass
class VoxSpotify:
    user_id: str
    token_info: Optional[dict] = None
    device_id: Optional[str] = None
    last_updated: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert dataclass to dictionary, handling datetime serialization"""
        result = asdict(self)
        if result['last_updated'] is not None:
            result['last_updated'] = result['last_updated'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VoxSpotify':
        """Create dataclass from dictionary, handling datetime parsing"""
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

