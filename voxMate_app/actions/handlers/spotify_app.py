# Required python imports
import spotipy
import time
import traceback
import requests
import traceback
from typing import Optional, Tuple
from rapidfuzz.fuzz import ratio
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
                logger.error("No valid token available")
                return False
            if 'access_token' not in token_info:
                    logger.error("Token missing access_token")
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
                logger.error(f"Spotify API test failed: {str(api_error)}")
                self.sp = None
                return False
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
            logger.error("Please login using the Web App and try again.")
            return None     
        try:
            doc = self.load_spotify_doc()
            if not doc or not doc.token_info:
                logger.warning("No token avaiable, please login to Spotify using the web app.")
                return None
            # Check if token needs refresh
            if time.time() > doc.token_info['expires_at']:
                logger.info("Refreshing expired token")
                oauth = self.create_spotify_oauth()
                if oauth is None:
                    logger.error("Spotify OAuth error")
                    return None
                new_token_info = oauth.refresh_access_token(doc.token_info['refresh_token'])
                if new_token_info is None:
                    logger.error("Token refresh failed")
                    return None
                
                # Update and save the document
                doc.token_info = new_token_info
                if not self.save_spotify_doc(doc):
                    logger.error("Failed to save refreshed token")
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
    

    def detect_spotify_type(self, query: str, artist: str, user_content_type: Optional[str] = None) -> Tuple[str, str]:
        """
        Try to determine if the query is a song, album, artist, playlist, or podcast.
        Returns:
            A tuple of (content_type, uri) or (None, None) if not found.
        """
        if not self.sp and not self.initialize_spotify():
            return None, None

        query_lower = query.strip().lower()
        artist_lower = artist.strip().lower() if artist else None

        try:
            # Construct the query string
            q = f'track:{query_lower} artist:{artist_lower}' if artist_lower else query_lower

            # If a user-specified type is given, search for it first
            if user_content_type in ["track", "playlist", "album", "artist"]:
                results = self.sp.search(q=q, type=user_content_type, limit=5)
                items = results.get(f"{user_content_type}s", {}).get("items", [])

                for item in items:
                    name = item.get("name", "").strip().lower()

                    # Exact match
                    if name == query_lower:
                        return user_content_type, item["uri"]

                    # Partial match
                    if query_lower in name:
                        logger.info(f"Partial match: '{query_lower}' in '{name}'")
                        return user_content_type, item["uri"]

                    # Fuzzy match
                    if ratio(query_lower, name) > 80:
                        logger.info(f"Fuzzy match ({ratio(query_lower, name)}%): '{query_lower}' vs '{name}'")
                        return user_content_type, item["uri"]

                # Fallback to first result if no match
                if items:
                    logger.info(f"No exact/partial/fuzzy match for '{query_lower}' in type '{user_content_type}'")
                    logger.info(f"Returning best available match: {items[0]['name']} [{user_content_type}]")
                    return user_content_type, items[0]["uri"]

            # Fallback: Try all types
            results = self.sp.search(q=q, type="track,album,artist,playlist", limit=5)
            type_priority = ["album", "artist", "track", "playlist"]

            for content_type in type_priority:
                items = results.get(f"{content_type}s", {}).get("items", [])
                for item in items:
                    name = item.get("name", "").strip().lower()

                    # Exact match
                    if name == query_lower:
                        return content_type, item["uri"]

                    # Partial match
                    if query_lower in name:
                        logger.info(f"Partial match: '{query_lower}' in '{name}'")
                        return content_type, item["uri"]

                    # Fuzzy match
                    if ratio(query_lower, name) > 80:
                        logger.info(f"Fuzzy match ({ratio(query_lower, name)}%): '{query_lower}' vs '{name}'")
                        return content_type, item["uri"]

            # Fallback: first available result
            for content_type in type_priority:
                items = results.get(f"{content_type}s", {}).get("items", [])
                if items:
                    logger.info(f"No strong match for '{query_lower}' — returning best available: {items[0]['name']} [{content_type}]")
                    return content_type, items[0]["uri"]

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


    def stop_playback(self) -> bool:
        """Stop playback while maintaining playback context"""
        if not self.sp and not self.initialize_spotify():
            return False    
        try:
            playback = self.sp.current_playback()
            if playback and playback['is_playing']:
                self.sp.pause_playback()
                return True
            return True  # No active playback is fine
        except spotipy.SpotifyException as e:
            if e.http_status in [404, 403]:  # Nothing is playing
                logger.warning("No active playback to stop")
                return True
            logger.error(f"Failed to stop playback: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error stopping playback: {e}")
            return False
 
 
    def handle_spotify_play(self, params: Dict) -> bool:
        """
        Main method to handle Spotify playback with full error handling.
        Args:
            cmd (Dict): Dictionary in format:
                {
                    "cmd": "spotify_play",
                    "params": query (optional),
                    "type": media_type (optional)
                }
        Returns:
            bool: True if playback was successfully started, False otherwise
        """
        if not self.sp and not self.initialize_spotify():
            message = "Spotify did not initialize, could not play Spotify"
            return False, message
        device_id = self.get_valid_device_id()
        if not device_id:
            logger.error("No valid playback device available")
            message = "No valid playback device available, could not play Spotify"
            return False, message
        logger.info(f"Attempting playback on device ID: {device_id}")
        # Transfer playback (with retry logic)
        if not self.transfer_playback(device_id):
            logger.error("Failed to transfer playback")
            message = "Failed to transfer playback, could not play Spotify"
            return False, message
        # Wait for transfer to complete with verification
        timeout = time.time() + 5  # 5 second timeout
        while time.time() < timeout:
            try:
                current_playback = self.sp.current_playback()
                if current_playback and current_playback.get('device', {}).get('id') == device_id:
                    break
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Error checking playback state: {e}")
        else:  # Executes if while loop completes without breaking
            logger.error("Playback transfer verification timed out")
            message = "Failed to transfer playback, could not play Spotify"
            return False, message
        query = params.get("query", None)
        artist = params.get("artist", None)
        user_content_type = params.get("type", None)
        logger.info(f"Handling Spotify play — query: {query}, user_type: {user_content_type}")
        # Handle search query and type if provided
        try:
            if query is not None:
                content_type, uri = self.detect_spotify_type(query, artist, user_content_type)
                # if user_content_type:
                #     content_type, uri = self.detect_spotify_type(query, artist, user_content_type)
                # elif user_content_type:
                #     content_type, uri = self.detect_spotify_type(query, artist, user_content_type)
                # else:
                #     content_type, uri = self.detect_spotify_type(query)
                logger.info(f"Spotify detect result - type: {content_type}, uri: {uri}")
                # if uri and isinstance(uri, str) and uri.startswith("spotify:"):
                #     # Case 1: Artist
                #     if content_type == "artist":
                #         self.sp.start_playback(device_id=device_id, context_uri=uri)
                #         logger.info(f"Playing artist: {query}")
                #     # Case 2: Track
                #     elif content_type == "track":
                #         # Play the track
                #         self.sp.start_playback(device_id=device_id, uris=[uri])
                #         logger.info(f"Playing track: {query}")
                #     # Case 3: Playlist/Album
                #     else:
                #         self.sp.start_playback(device_id=device_id, context_uri=uri)
                #         logger.info(f"Playing {content_type}: {query}")
                #     return True, None
                        # Step 1: Get current queue
                save_queue_start = time.time()
                current_queue = self.sp.queue()
                saved_tracks = [item["uri"] for item in current_queue.get("queue", [])]
                save_queue_end = time.time() - save_queue_start

                logger.info("Saved queue: ", saved_tracks)

                add_request_start = time.time()
                # Step 2: Start playing the requested content
                if content_type == "track":
                    self.sp.start_playback(device_id=device_id, uris=[uri])
                    logger.info(f"Playing track: {query}")
                elif content_type in ["album", "playlist"]:
                    self.sp.start_playback(device_id=device_id, context_uri=uri)
                    logger.info(f"Playing {content_type}: {query}")
                elif content_type == "artist":
                    self.sp.start_playback(device_id=device_id, context_uri=uri)
                    logger.info(f"Playing artist: {query}")
                add_request_end = time.time() - add_request_start

                # Optional: wait briefly for playback to update (Spotify can lag)
                # import time
                # time.sleep(1)

                re_add_queue_start = time.time()
                # Step 3: Re-add previous queue
                for track_uri in saved_tracks:
                    self.sp.add_to_queue(track_uri, device_id=device_id)
                    logger.info(f"Re-added to queue: {track_uri}")
                re_add_queue_end = time.time() - re_add_queue_start

                logger.info("\n Spotify playing times:")
                logger.info(f"Saving queue: {save_queue_end:.2f}s")
                logger.info(f"Playing request: {add_request_end:.2f}s")
                logger.info(f"Re-add queue: {re_add_queue_end:.2f}s")

                return True, None
            else:
                logger.warning(f"Could not resolve Spotify URI for query: '{query}' — attempting to resume playback")
        except Exception as e:
            logger.error(f"Playback error: {e}")
            logger.info("Falling back to generic playback")
        #  If no query given just resume playback
        try:
            self.sp.start_playback(device_id=device_id)
            logger.info("Resumed playback successfully")
            return True, None
        except spotipy.SpotifyException as e:
            if e.http_status in [403, 404]:
                # If nothing is playing, start a default playlist
                self.sp.start_playback(
                    device_id=device_id,
                    context_uri="spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"  # Today's Top Hits
                )
                logger.info("Started default playlist")
                return True, None
            logger.error(f"Playback resume error: {e}")
            message = "Spotify has had an error"
            return False, message
            
    
    def load_spotify_doc(self) -> Optional[VoxSpotify]:
        """Load the full VoxSpotify document as a dataclass"""
        try:
            if (mongodb := load_mongodb()) is None:
                return None  # Connection error already logged 
            if (doc := mongodb.voxSpotify.find_one({'user_id': self.user_id})) is None:
                logger.info(f"No Spotify document for user {self.user_id}")
                return None
            return VoxSpotify.from_dict(doc) if doc else None
        except KeyError as e:
            logger.error(f"Missing required field in document: {e}")
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