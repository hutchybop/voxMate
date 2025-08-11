# Required python imports
import spotipy
import time
from typing import Optional, Tuple, Dict
from datetime import datetime, timezone
from spotipy.oauth2 import SpotifyOAuth
from threading import Lock
from rapidfuzz.fuzz import ratio

# Required local imports
import config.constraints as constraints
from utils.logging import logger
from config.settings import load_user, load_mongodb
from models.models import VoxSpotify


class SpotifyPlayer:
    """
    Optimized Spotify player with device caching and consistent error handling.
    Features:
    - Automatic device discovery and caching
    - Memory and database fallback
    - Token validation
    - Retry logic
    - Graceful degradation
    """

    _instance = None
    _lock = Lock()
    

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    

    def __init__(self, max_retries: int = 2) -> None:
        self.SPOTIFY_CLIENT_ID = constraints.SPOTIFY_CLIENT_ID
        self.SPOTIFY_CLIENT_SECRET = constraints.SPOTIFY_CLIENT_SECRET
        self.user_id = load_user().get("user_id")
        self.max_retries = max_retries
        self.memory_cache = {'device_id': None, 'last_updated': None}
        self.sp = None
        self._initialized = True


    def _handle_spotify_error(self, operation: str, error: Exception, default_msg: str = None) -> Tuple[bool, Optional[str]]:
        """Centralized error handling that always returns (bool, str) tuple"""
        error_msg = f"Spotify {operation} failed: {str(error)}"
        logger.error(error_msg)
        
        # Return appropriate tuple based on error type
        if isinstance(error, spotipy.SpotifyException):
            if error.http_status == 403:
                return False, "Permission denied - please check your Spotify account"
            elif error.http_status == 404:
                return False, "Resource not found"
            elif "Restriction violated" in str(error):
                return False, str(error)  # Preserve Spotify's user-friendly messages
        
        # For other errors, use the provided default or generic message
        return False, default_msg or f"Spotify operation failed: {operation}"


    def initialize_spotify(self) -> bool:
        """Initialize Spotify client with consistent error handling"""
        try:
            token_info = self.load_spotify_token()
            if not token_info or 'access_token' not in token_info:
                logger.error("No valid token available")
                return False

            self.sp = spotipy.Spotify(
                auth=token_info['access_token'],
                requests_timeout=10,
                retries=self.max_retries,
                status_forcelist=[500, 502, 503, 504]
            )

            # Verify connection
            self.sp.me()
            return True
        except Exception as e:
            self.sp = None
            return self._handle_spotify_error("initialization", e)


    def create_spotify_oauth(self) -> Optional[SpotifyOAuth]:
        """Create SpotifyOAuth to authorize the user's Spotify account"""
        try:
            if (mongodb := load_mongodb()) is None:
                return None
            state = mongodb.users.find_one({"user_id": self.user_id}).get("api_token", "")
            return SpotifyOAuth(
                client_id=self.SPOTIFY_CLIENT_ID,
                client_secret=self.SPOTIFY_CLIENT_SECRET,
                redirect_uri='https://voxmate.longrunner.co.uk/voxSpotify/callback',
                scope=constraints.SCOPES,
                cache_handler=None,
                state=state
            )
        except Exception as e:
            self._handle_spotify_error("OAuth creation", e)
            return None


    def load_spotify_token(self) -> Optional[dict]:
        """Load and refresh Spotify token if needed"""
        if not self.user_id:
            logger.error("User not logged in")
            return None

        try:
            doc = self.load_spotify_doc()
            if not doc or not doc.token_info:
                logger.warning("No token available, please login to Spotify")
                return None

            if time.time() > doc.token_info['expires_at']:
                logger.info("Refreshing expired token")
                if (oauth := self.create_spotify_oauth()) is None:
                    return None
                
                if not (new_token_info := oauth.refresh_access_token(doc.token_info['refresh_token'])):
                    logger.error("Token refresh failed")
                    return None
                
                doc.token_info = new_token_info
                if not self.save_spotify_doc(doc):
                    logger.error("Failed to save refreshed token")
                return new_token_info
            return doc.token_info
        except Exception as e:
            self._handle_spotify_error("token loading", e)
            return None


    def _retry_operation(self, operation, *args, **kwargs) -> None:
        """Generic retry logic for Spotify operations"""
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries:
                    raise
                time.sleep(1 * (attempt + 1))


    def find_device_id_by_name(self, name_substring: str) -> Tuple[Optional[str], Optional[str]]:
        """Find device ID by name substring with retry logic"""
        try:
            devices = self._retry_operation(self.sp.devices).get('devices', [])
            for device in devices:
                if name_substring.lower() in device['name'].lower():
                    return device['id'], device['name']
            return None, None
        except Exception as e:
            self._handle_spotify_error("device search", e)
            return None, None


    def refresh_device_cache(self) -> Optional[str]:
        """Refresh the device cache and return active device ID"""
        try:
            current_devices = self.sp.devices().get('devices', [])
            mem_id = self.memory_cache.get('device_id')
            return mem_id if mem_id and any(d['id'] == mem_id for d in current_devices) else None
        except Exception as e:
            self._handle_spotify_error("device cache refresh", e)
            return None


    def get_valid_device_id(self, preferred_device_name: str = 'voxMate Pi') -> Optional[str]:
        """Get a valid device ID with fallback logic"""
        if not self.sp and not self.initialize_spotify():
            return None

        # Check memory cache first
        if active_device := self.refresh_device_cache():
            return active_device

        # Try to find device by name
        new_id, new_name = self.find_device_id_by_name(preferred_device_name)
        if new_id:
            self.memory_cache.update({
                'device_id': new_id,
                'last_updated': time.time()
            })
            self.update_cached_device_id_in_db(new_id)
            logger.info(f"Found active device: {new_name}")
            return new_id

        # Fall back to database cache
        if db_id := self.load_cached_device_id_from_db():
            self.memory_cache.update({
                'device_id': db_id,
                'last_updated': time.time()
            })
            logger.warning("Using database-cached device ID - device may not be active")
            return db_id

        logger.error("No usable device found")
        return None


    def _match_spotify_item(self, query: str, items: list, content_type: str) -> Optional[Tuple[str, str]]:
        """Helper method to find matching Spotify items"""
        query_lower = query.strip().lower()
        for item in items:
            name = item.get("name", "").strip().lower()
            if name == query_lower:
                logger.info(f"Exact match: '{query}' in '{name}', type '{content_type}'")
                return content_type, item["uri"]
            if query_lower in name:
                logger.info(f"Partial match: '{query}' in '{name}'")
                return content_type, item["uri"]
            if ratio(query_lower, name) > 80:
                logger.info(f"Fuzzy match ({ratio(query_lower, name)}%): '{query}' vs '{name}'")
                return content_type, item["uri"]
        return None


    def detect_spotify_type(self, query: str, artist: str, user_content_type: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Determine if the query is a song, album, artist, playlist, or podcast"""
        if not self.sp and not self.initialize_spotify():
            return None, None

        query_lower = query.strip().lower()
        artist_lower = artist.strip().lower() if artist else None
        q = f'track:{query_lower} artist:{artist_lower}' if artist_lower else query_lower

        try:
            # Try user-specified type first
            if user_content_type in ["track", "playlist", "album", "artist"]:
                results = self.sp.search(q=q, type=user_content_type, limit=5)
                items = results.get(f"{user_content_type}s", {}).get("items", [])
                if match := self._match_spotify_item(query_lower, items, user_content_type):
                    return match
                if items:  # Fallback to first result
                    logger.info(f"No strong match - returning best available: {items[0]['name']} [{user_content_type}]")
                    return user_content_type, items[0]["uri"]

            # Fallback: Try all types
            results = self.sp.search(q=q, type="track,album,artist,playlist", limit=5)
            for content_type in ["album", "artist", "track", "playlist"]:
                items = results.get(f"{content_type}s", {}).get("items", [])
                if match := self._match_spotify_item(query_lower, items, content_type):
                    return match
                if items:  # Fallback to first result
                    logger.info(f"No strong match - returning best available: {items[0]['name']} [{content_type}]")
                    return content_type, items[0]["uri"]
        except Exception as e:
            self._handle_spotify_error("type detection", e)
        
        return None, None


    def transfer_playback(self, device_id: str) -> bool:
        """Safely transfer playback to a device with retry logic"""
        try:
            self._retry_operation(
                self.sp.transfer_playback,
                device_id=device_id,
                force_play=False
            )
            return True
        except Exception as e:
            return self._handle_spotify_error("playback transfer", e)


    def _verify_playback_transfer(self, device_id: str, timeout: int = 5) -> bool:
        """Verify playback transfer completed successfully"""
        start_time = time.time()
        while time.time() < start_time + timeout:
            try:
                if (current := self.sp.current_playback()) and current.get('device', {}).get('id') == device_id:
                    return True
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Error checking playback state: {e}")
        return False


    def _build_fallback_queue(self, device_id: str) -> None:
        """Build a fallback queue with top tracks"""
        try:
            # Add user's top tracks
            top_tracks = self.sp.current_user_top_tracks(limit=10, time_range="short_term")["items"]
            for track in top_tracks:
                self.sp.add_to_queue(track["uri"], device_id=device_id)
                logger.info(f"Added top track to queue: {track['name']}")
        except Exception as e:
            logger.warning(f"Failed to build fallback queue: {e}")


    def handle_spotify_play(self, params: Dict) -> Tuple[bool, Optional[str]]:
        """Main method to handle Spotify playback with consistent error handling"""
        try:
            # Initialize Spotify
            if not self.sp and not self.initialize_spotify():
                return False, "Spotify initialization failed"

            # Get device ID
            if not (device_id := self.get_valid_device_id()):
                return False, "No valid playback device available"

            # Transfer playback
            if not self.transfer_playback(device_id):
                return False, "Failed to transfer playback"

            if not self._verify_playback_transfer(device_id):
                return False, "Playback transfer verification timed out"

            # Set volume and handle playback
            self.sp.volume(100, device_id=device_id)
            query = params.get("query", "")
            artist = params.get("artist", "")
            user_content_type = params.get("type", "")

            if not query:  # Resume playback if no query
                try:
                    self._handle_track_playback(device_id=device_id)
                    return True, None
                except Exception:
                    return self._start_fallback_playback(device_id)
            
            if query == "news":
                show_uri = "spotify:show:2qZ0xpaBBwf3bTYhA10KZY"
                try:
                    episodes = self.sp.show_episodes(show_uri, limit=1)
                    if not episodes['items']:
                        return False, "No news episodes found"

                    episode_uri = episodes['items'][0]['uri']
                    self.sp.add_to_queue(uris=[episode_uri])
                    self.sp.next_track()
                    self.sp.start_playback(device_id=device_id)
####### Play the news only.........
                    return True, None
                except Exception as e:
                    return self._handle_spotify_error("news podcast playback", e), "Error getting news podcast"

            # Handle playback with query
            content_type, uri = self.detect_spotify_type(query, artist, user_content_type)
            if not uri:
                return self._start_fallback_playback(device_id)

            try:
                if content_type in ["album", "playlist", "artist"]:
                    self.sp.start_playback(device_id=device_id, context_uri=uri)
                    return True, None

                if content_type == "track":
                    self._handle_track_playback(device_id, uri)
                    return True, None
            except Exception as e:
                logger.error(f"Playback error: {e}")
                return self._start_fallback_playback(device_id)
        except Exception as e:
            return self._handle_spotify_error(
                "playback",
                e,
                "Failed to start playback"
            )


    def _handle_track_playback(self, device_id: str, uri: str = None) -> None:
        """Handle track playback with queue management"""
        try:
            has_queue = bool(self.sp.queue().get("queue"))
        except Exception:
            has_queue = False

        if uri:
            self.sp.add_to_queue(uri, device_id=device_id)
            if has_queue:
                self.sp.next_track()

        if not has_queue:
            self._build_fallback_queue(device_id)

        self.sp.start_playback(device_id=device_id)

    def _start_fallback_playback(self, device_id: str) -> Tuple[bool, str]:
        """Start fallback playback with top tracks or default playlist"""
        try:
            self._build_fallback_queue(device_id)
            self.sp.start_playback(device_id=device_id)
            return True, None
        except Exception:
            try:
                self.sp.start_playback(
                    device_id=device_id,
                    context_uri="spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"
                )
                return True, None
            except Exception as e:
                return False, "Could not resume or start fallback playlist"
            

    # Simplified playback control methods
    def _basic_playback_control(self, operation: str, success_msg: str = None, error_msg: str = None) -> Tuple[bool, Optional[str]]:
        """Generic method for basic playback controls with consistent returns"""
        if not self.sp and not self.initialize_spotify():
            return False, "Spotify initialization failed"

        try:
            if not (playback := self.sp.current_playback()) or not playback.get("item"):
                return False, "No active playback"

            getattr(self.sp, operation)()
            return True, success_msg
        except Exception as e:
            return self._handle_spotify_error(operation, e, error_msg)
        

    def stop_playback(self) -> Tuple[bool, Optional[str]]:
        return self._basic_playback_control(
            "pause_playback",
            error_msg="Failed to stop playback"
        )


    def skip_playback(self) -> Tuple[bool, Optional[str]]:
        return self._basic_playback_control(
            "next_track", 
            error_msg="Failed to skip track"
        )


    def repeat_playback(self, repeat) -> Tuple[bool, Optional[str]]:
        try:
            if not self.sp and not self.initialize_spotify():
                return False, "Spotify initialization failed"
            
            self.sp.repeat(state=repeat)
            return True, None
        except Exception as e:
            return self._handle_spotify_error(
                "repeat toggle", 
                e,
                "Failed to toggle repeat mode"
            )


    def shuffle_playback(self, shuffle) -> Tuple[bool, Optional[str]]:
        try:
            if not self.sp and not self.initialize_spotify():
                return False, "Spotify initialization failed"
            
            self.sp.shuffle(state=shuffle)
            return True, None
        except spotipy.SpotifyException as e:
            if "Restriction violated" in str(e):
                return False, str(e)  # Preserve Spotify's user-friendly message
            return self._handle_spotify_error(
                "shuffle toggle",
                e,
                "Failed to toggle shuffle mode"
            )
        except Exception as e:
            return self._handle_spotify_error(
                "shuffle toggle", 
                e,
                "Failed to toggle shuffle mode"
            )


    # Database operations
    def load_spotify_doc(self) -> Optional[VoxSpotify]:
        """Load the full VoxSpotify document as a dataclass"""
        try:
            if (mongodb := load_mongodb()) is None:
                return None
            if (doc := mongodb.voxSpotify.find_one({'user_id': self.user_id})) is None:
                logger.info(f"No Spotify document for user {self.user_id}")
                return None
            return VoxSpotify.from_dict(doc)
        except Exception as e:
            self._handle_spotify_error("document loading", e)
            return None


    def save_spotify_doc(self, doc: VoxSpotify) -> bool:
        """Save the VoxSpotify dataclass to MongoDB"""
        try:
            if (mongodb := load_mongodb()) is None:
                return False
            mongodb.voxSpotify.update_one(
                {'user_id': self.user_id},
                {'$set': doc.to_dict()},
                upsert=True
            )
            return True
        except Exception as e:
            self._handle_spotify_error("document saving", e)
            return False


    # Device cache methods
    def load_cached_device_id_from_db(self) -> Optional[str]:
        doc = self.load_spotify_doc()
        return doc.device_id if doc else None


    def update_cached_device_id_in_db(self, new_id: str) -> bool:
        doc = self.load_spotify_doc() or VoxSpotify(user_id=self.user_id)
        doc.device_id = new_id
        doc.last_updated = datetime.now(timezone.utc)
        return self.save_spotify_doc(doc)