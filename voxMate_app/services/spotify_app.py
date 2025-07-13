# Required python imports
import spotipy
import time
import traceback
import requests
import traceback
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from spotipy.oauth2 import SpotifyOAuth
from threading import Lock

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


    # Control class state creatation with thread locking protection
    _instance = None  # Class-level instance reference
    _lock = Lock()
    

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    

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
        self._initialized = True  # Mark as initialized
        

    def initialize_spotify(self) -> bool:
        """Initialize Spotify client with comprehensive error handling"""
        try:
            token_info = self.load_spotify_token()
            if token_info is None:
                logger.error("Failed to initialize Spotify, no valid token available")
                return False
            if 'access_token' not in token_info:
                    logger.error("Failed to initialize Spotify, Token missing access_token")
                    return False
            # Initialize client with retry configuration
            self.sp = spotipy.Spotify(
                auth=token_info['access_token'],
                requests_timeout=10,
                retries=self.max_retries,
                status_forcelist=[500, 502, 503, 504]
            )
            # Verify connection with a simple API call
            try:
                self.sp.me()  # Gets current user profile
                return True
            except Exception as api_error:
                logger.error(f"Failed to initialize Spotify, Spotify API test failed: {str(api_error)}")
                self.sp = None
                return False
        except spotipy.SpotifyException as e:
            logger.error(f"Failed to initialize Spotify, Spotify API error: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to initialize Spotify, Network error: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize Spotify, Unexpected initialization error: {e}")
            traceback.print_exc()
        self.sp = None  # Ensure clean state on failure
        return False


    def create_spotify_oauth(self) -> SpotifyOAuth:
        """Create the SpotifyOAuth to authorise the user Spotify account"""
        if (mongodb := load_mongodb()) is None:
            return None  # Connection error already logged
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
            logger.error("Failed to load Spotify Token, please login using the Web App and try again.")
            return None     
        try:
            doc = self.load_spotify_doc()
            if not doc or not doc.token_info:
                logger.warning("Failed to load Spotify Token, no token avaiable, please login to Spotify using the web app.")
                return None
            # Check if token needs refresh
            if time.time() > doc.token_info['expires_at']:
                logger.info("Loading Spotify Token, refreshing expired token")
                oauth = self.create_spotify_oauth()
                if oauth is None:
                    logger.error("Failed to load Spotify Token, Spotify OAuth error")
                    return None
                new_token_info = oauth.refresh_access_token(doc.token_info['refresh_token'])
                if new_token_info is None:
                    logger.error("Failed to load Spotify Token, Token refresh failed")
                    return None
                
                # Update and save the document
                doc.token_info = new_token_info
                if not self.save_spotify_doc(doc):
                    logger.error("Failed to load Spotify Token, failed to save refreshed token")
                return new_token_info
            return doc.token_info
        except Exception as e:
            logger.error(f"Failed to load Spotify Token: {str(e)}", exc_info=True)
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
                logger.error(f"Find device id by name failed, attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    traceback.print_exc()
        return None, None
    

    def refresh_device_cache(self) -> Optional[str]:
        """Refresh the device cache and return the active device ID"""
        current_devices = []
        try:
            current_devices = self.sp.devices().get('devices', [])
        except Exception as e:
            logger.error(f"Refreshing device cache failed, failed to get current devices: {e}")
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
            logger.info(f"Getting valid device id, found active device: {new_name}")
            return new_id
        # Fall back to database cache if available
        db_id = self.load_cached_device_id_from_db()
        if db_id:
            self.memory_cache['device_id'] = db_id
            self.memory_cache['last_updated'] = time.time()
            logger.warning("Failed to get valid device id, using database-cached device ID - device may not be active")
            return db_id
        logger.error("Failed to get valid device id, no usable device found")
        return None
    

    def detect_spotify_type(self, query: str) -> Tuple[str, str]:
        """Try to determine if the query is a song, album, artist, playlist, or podcast."""
        if not self.sp and not self.initialize_spotify():
            return False
        try:
            result = self.sp.search(q=query, type="track,album,artist,playlist,show", limit=1)
            if result['tracks']['items']:
                return "track", result['tracks']['items'][0]['uri']
            if result['albums']['items']:
                return "album", result['albums']['items'][0]['uri']
            if result['artists']['items']:
                return "artist", result['artists']['items'][0]['uri']
            if result['playlists']['items']:
                return "playlist", result['playlists']['items'][0]['uri']
            if result['shows']['items']:  # Podcasts
                return "show", result['shows']['items'][0]['uri']
        except Exception as e:
            logger.error(f"Failed to detect Spotify type: {e}")
        return None, None
    

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
                logger.error(f"Failed to transfer playback, transfer attempt {attempt + 1} failed: {e}")
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
                    logger.error("Failed to start playback, device not found - may be offline")
                    return False
                logger.error(f"Failed to start playback, dlayback attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    traceback.print_exc()
                time.sleep(1 * (attempt + 1))
            except Exception as e:
                logger.error(f"Failed to start playback, unexpected playback error: {e}")
                traceback.print_exc()
                return False
        return False


    def stop_playback(self) -> bool:
        """Stop playback while maintaining playback context"""
        if not self.sp and not self.initialize_spotify():
            return False    
        try:
            self.sp.pause_playback()
            return True
        except Exception as e:
            logger.error(f"Failed to stop playback: {e}")
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
            return False
        device_id = self.get_valid_device_id()
        if not device_id:
            logger.error("No valid playback device available")
            return False
        logger.info(f"Attempting playback on device ID: {device_id}")
        # Transfer playback (with retry logic)
        if not self.transfer_playback(device_id):
            logger.error("Failed to handle Spotify play, failed to transfer playback")
            return False
        # Wait for transfer to complete with verification
        timeout = time.time() + 5  # 5 second timeout
        while time.time() < timeout:
            try:
                current_playback = self.sp.current_playback()
                if current_playback and current_playback.get('device', {}).get('id') == device_id:
                    break
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Failed to handle Spotify play, error checking playback state: {e}")
        else:  # This goes here - executes if while loop completes without breaking
            logger.error("Failed to handle Spotify play,, playback transfer verification timed out")
            return False
        query = ""
        if isinstance(params, str):
            query = params.strip()
        elif isinstance(params, dict):
            query = params.get("query", "").strip()
        # Handle empty query (resume playback)
        if not query:
            try:
                # First try to resume existing playback
                self.sp.start_playback(device_id=device_id)
                logger.info("Handling Spotify play, resumed playback successfully")
                return True
            except spotipy.SpotifyException as e:
                if e.http_status == 404:
                    # If nothing is playing, start a default playlist
                    self.sp.start_playback(
                        device_id=device_id,
                        context_uri="spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"  # Today's Top Hits
                    )
                    logger.info("Handling Spotify play, started default playlist")
                    return True
                logger.error(f"Failed to handle spotify play, playback resume error: {e}")
                return False
        # Handle search query
        try:
            content_type, uri = self.detect_spotify_type(query)
            if not uri:
                return False
            # Always use context_uri for continuous playback
            if content_type in ["track", "album", "playlist", "show", "artist"]:
                self.sp.start_playback(
                    device_id=device_id,
                    context_uri=uri,
                    offset={"position": 0} if content_type == "track" else None
                )
                logger.info(f"Handling Spotify Play, started playing {content_type} context: {query}")
                return True
        except Exception as e:
            logger.error(f"Failed to handle spotify play, playback error: {e}")
            return False

    
    def load_spotify_doc(self) -> Optional[VoxSpotify]:
        """Load the full VoxSpotify document as a dataclass"""
        try:
            if (mongodb := load_mongodb()) is None:
                return None  # Connection error already logged 
            if (doc := mongodb.voxSpotify.find_one({'user_id': self.user_id})) is None:
                logger.info(f"Failed to load VoxSpotify document, no Spotify document for user {self.user_id}")
                return None
            return VoxSpotify.from_dict(doc) if doc else None
        except KeyError as e:
            logger.error(f"Failed to load VoxSpotify document, missing required field in document: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load VoxSpotify document: {e}")
            return None
    

    def save_spotify_doc(self, doc: VoxSpotify) -> bool:
        """Save the VoxSpotify dataclass to MongoDB"""
        try:
            if (mongodb := load_mongodb()) is None:
                return None  # Connection error already logged
            mongodb.voxSpotify.update_one(
                {'user_id': self.user_id},
                {'$set': doc.to_dict()},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save VoxSpotify document: {e}")
            return False