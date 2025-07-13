
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class VoxSpotify:
    user_id: str
    token_info: Optional[Dict[str, Any]] = None
    device_id: Optional[str] = None
    last_updated: Optional[datetime] = None
    user_code: Optional[str] = None

    def __post_init__(self):
        """Handle MongoDB _id and type conversions"""
        # Remove MongoDB-specific fields
        self.__dict__.pop('_id', None)
        # Ensure last_updated is either None or datetime
        if isinstance(self.last_updated, str):
            try:
                self.last_updated = datetime.fromisoformat(self.last_updated)
            except ValueError as e:
                logger.warning(f"Failed to parse last_updated: {e}")
                self.last_updated = None


    def to_dict(self) -> dict:
        """Convert to dictionary with ISO-formatted datetime"""
        result = asdict(self)
        if result['last_updated'] is not None:
            result['last_updated'] = result['last_updated'].isoformat()
        return result


    @classmethod
    def from_dict(cls, data: dict) -> 'VoxSpotify':
        """Safe constructor with complete type handling"""
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary") 
        try:
            return cls(
                user_id=str(data['user_id']),  # Force string conversion
                token_info=data.get('token_info') if isinstance(data.get('token_info'), dict) else None,
                device_id=str(data.get('device_id')) if data.get('device_id') is not None else None,
                last_updated=data.get('last_updated'),  # Handled in __post_init__
                user_code=str(data.get('user_code')) if data.get('user_code') is not None else None
            )
        except KeyError as e:
            logger.error(f"Missing required field: {e}")
            raise ValueError(f"Missing required field: {e}") from None