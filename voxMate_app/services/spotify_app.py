# Required python imports
import spotipy
import time
import traceback
import requests
import traceback
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from spotipy.oauth2 import SpotifyOAuth

# Required local imports
import config.constrants as constrants
from utils.logging import logger
from config.settings import load_user
from models.models import VoxSpotify
from config.settings import load_mongodb


class SpotifyPlayer:
    """
    Spotify player with device caching and comprehensive error handling.
    Features:
    - Automatic device discovery and caching
    - Memory and database fallback
    - Token validation
    - Retry logic
    - Graceful degradation
    """
    
    def __init__(self, max_retries: int = 2):
        """
        Initialize the Spotify player.
        
        Args:
            user_id: Unique identifier for the current user
            max_retries: Maximum number of retry attempts for API calls
        """
        self.SPOTIFY_CLIENT_ID = constrants.SPOTIFY_CLIENT_ID
        self.SPOTIFY_CLIENT_SECRET = constrants.SPOTIFY_CLIENT_SECRET
        self.user_id = load_user().get("user_id", None)
        self.max_retries = max_retries
        self.memory_cache = {'device_id': None, 'last_updated': None}
        self.sp = None  # Will be initialized when needed
        
    def initialize_spotify(self) -> bool:
        """Initialize Spotify client with comprehensive error handling"""
        try:
            token_info = self.load_spotify_token()
                
            # Initialize client with retry configuration
            self.sp = spotipy.Spotify(
                auth=token_info['access_token'],
                requests_timeout=10,
                retries=self.max_retries,
                status_forcelist=[500, 502, 503, 504]
            )
            
            # Verify connection with a simple API call
            self.sp.me()  # Gets current user profile
            return True
            
        except spotipy.SpotifyException as e:
            logger.error(f"Spotify API error: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected initialization error: {e}")
            traceback.print_exc()
            
        self.sp = None  # Ensure clean state on failure
        return False

    def create_spotify_oauth(self) -> SpotifyOAuth:
        """Create the SpotifyOAuth to authorise the user Spotify account"""
        mongodb = load_mongodb()
        state = mongodb.users.find_one({"user_id": self.user_id}).get("api_token" "")

        return SpotifyOAuth(
            client_id=constrants.SPOTIFY_CLIENT_ID,
            client_secret=constrants.SPOTIFY_CLIENT_SECRET,
            redirect_uri='https://voxmate.longrunner.co.uk/voxSpotify/callback',
            scope=constrants.SCOPES,
            cache_handler=None,
            state=state
        )
    
    def load_spotify_token(self) -> Optional[dict]:
        """Updated version using dataclass"""
        if not self.user_id:
            logger.error("Please login using the Web App and try again.")
            return None

        doc = self.load_spotify_doc()
        if not doc or not doc.token_info:
            return None
            
        try:
            if time.time() > doc.token_info['expires_at']:
                oauth = self.create_spotify_oauth()
                new_token_info = oauth.refresh_access_token(doc.token_info['refresh_token'])
                if not new_token_info:
                    return None
                
                # Update and save the document
                doc.token_info = new_token_info
                self.save_spotify_doc(doc)
                return new_token_info
                
            return doc.token_info
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    def load_cached_device_id_from_db(self) -> Optional[str]:
        """Updated version using dataclass"""
        doc = self.load_spotify_doc()
        return doc.device_id if doc else None
    
    def update_cached_device_id_in_db(self, new_id: str) -> bool:
        """Updated version using dataclass"""
        doc = self.load_spotify_doc() or VoxSpotify(user_id=self.user_id)
        doc.device_id = new_id
        doc.last_updated = datetime.now(timezone.utc)
        return self.save_spotify_doc(doc)
    
    def find_device_id_by_name(self, name_substring: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Find device ID by name substring with retry logic
        
        Returns:
            Tuple of (device_id, device_name) or (None, None) if not found
        """
        for attempt in range(self.max_retries + 1):
            try:
                devices = self.sp.devices().get('devices', [])
                for device in devices:
                    if name_substring.lower() in device['name'].lower():
                        return device['id'], device['name']
                
                if attempt < self.max_retries:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                    
            except Exception as e:
                logger.error(f"Device lookup attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    traceback.print_exc()
                
        return None, None
    
    def refresh_device_cache(self) -> Optional[str]:
        """Refresh the device cache and return the active device ID"""
        current_devices = []
        try:
            current_devices = self.sp.devices().get('devices', [])
        except Exception as e:
            logger.error(f"Failed to get current devices: {e}")
            return None
            
        # Check if memory cache device is still active
        mem_id = self.memory_cache.get('device_id')
        if mem_id and any(d['id'] == mem_id for d in current_devices):
            return mem_id
            
        return None
    
    def get_valid_device_id(self, preferred_device_name: str = 'voxMate Pi') -> Optional[str]:
        """
        Get a valid device ID with fallback logic.
        
        Priority:
        1. Currently active memory-cached device
        2. New lookup by device name
        3. Database-cached device
        
        Returns:
            str: Device ID if found, None otherwise
        """
        if not self.sp and not self.initialize_spotify():
            return None
            
        # First try to refresh cache with currently active devices
        active_device = self.refresh_device_cache()
        if active_device:
            return active_device
            
        # Try to find device by name
        new_id, new_name = self.find_device_id_by_name(preferred_device_name)
        if new_id:
            self.memory_cache['device_id'] = new_id
            self.memory_cache['last_updated'] = time.time()
            self.update_cached_device_id_in_db(new_id)
            logger.info(f"Found active device: {new_name}")
            return new_id
            
        # Fall back to database cache if available
        db_id = self.load_cached_device_id_from_db()
        if db_id:
            self.memory_cache['device_id'] = db_id
            self.memory_cache['last_updated'] = time.time()
            logger.warning("Using database-cached device ID - device may not be active")
            return db_id
            
        logger.error("No usable device found")
        return None
    
    def transfer_playback(self, device_id: str) -> bool:
        """Safely transfer playback to a device with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                self.sp.transfer_playback(
                    device_id=device_id,
                    force_play=False  # Safer than force_play=True
                )
                return True
            except Exception as e:
                logger.error(f"Transfer attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    traceback.print_exc()
                time.sleep(1 * (attempt + 1))
        return False
    
    def start_playback(self, device_id: str) -> bool:
        """Safely start playback with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                self.sp.start_playback(device_id=device_id)
                return True
            except spotipy.SpotifyException as e:
                if e.http_status == 404:
                    logger.error("Device not found - may be offline")
                    return False
                logger.error(f"Playback attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    traceback.print_exc()
                time.sleep(1 * (attempt + 1))
            except Exception as e:
                logger.error(f"Unexpected playback error: {e}")
                traceback.print_exc()
                return False
        return False
    
    def handle_spotify_play(self, params: Dict[str, Any]) -> bool:
        """
        Main method to handle Spotify playback with full error handling.
        
        Args:
            params: Dictionary of playback parameters
            
        Returns:
            bool: True if playback was successfully started, False otherwise
        """
        if not self.sp and not self.initialize_spotify():
            logger.error("Spotify initialization failed")
            return False
            
        device_id = self.get_valid_device_id()
        if not device_id:
            logger.error("No valid playback device available")
            return False
            
        logger.info(f"Attempting playback on device ID: {device_id}")
        
        # Transfer playback (with retry logic)
        if not self.transfer_playback(device_id):
            logger.error("Failed to transfer playback")
            return False
            
        # Small delay to ensure transfer completes
        time.sleep(2)
        
        # Start playback (with retry logic)
        if not self.start_playback(device_id):
            logger.error("Failed to start playback")
            return False
            
        logger.info("Playback started successfully")
        return True
    
    def load_spotify_doc(self) -> Optional[VoxSpotify]:
        """Load the full VoxSpotify document as a dataclass"""
        try:
            mongodb = load_mongodb()
            if not mongodb:
                return None
                
            doc = mongodb.voxSpotify.find_one({'user_id': self.user_id})
            return VoxSpotify.from_dict(doc) if doc else None
        except Exception as e:
            logger.error(f"Failed to load VoxSpotify document: {e}")
            return None
    
    def save_spotify_doc(self, doc: VoxSpotify) -> bool:
        """Save the VoxSpotify dataclass to MongoDB"""
        try:
            mongodb = load_mongodb()
            if not mongodb:
                return False
                
            mongodb.voxSpotify.update_one(
                {'user_id': self.user_id},
                {'$set': doc.to_dict()},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save VoxSpotify document: {e}")
            return False