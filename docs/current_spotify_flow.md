# voxMate Spotify Flow Documentation

## Overview
voxMate provides voice-controlled Spotify playback through a sophisticated AI-powered system that handles natural language requests and converts them into precise Spotify API commands.

## Supported Spotify Requests

### 1. **Playback Control**
- **Play/Resume**: `"Play music"`, `"Resume playback"`
- **Stop**: `"Stop music"`, `"Pause music"`, `"Stop the music"`
- **Skip**: `"Skip song"`, `"Next track"`, `"Skip this track"`

### 2. **Music Discovery & Playback**
- **General Play**: `"Play jazz music"`, `"Play some rock"`
- **Specific Track**: `"Play Thunderstruck by AC/DC"`, `"Play Bohemian Rhapsody"`
- **Artist Play**: `"Play The Beatles"`, `"Play some Taylor Swift"`
- **Album Play**: `"Play the album Abbey Road"`, `"Play Thriller album"`
- **Playlist Play**: `"Play my workout playlist"`, `"Play jazz playlist"`

### 3. **Playback Modes**
- **Repeat Control**:
  - `"Turn on repeat"` → Repeats entire context (album/playlist)
  - `"Repeat track"` → Repeats current track
  - `"Turn off repeat"` → Disables repeat
- **Shuffle Control**:
  - `"Turn on shuffle"` → Enables shuffle mode
  - `"Turn off shuffle"` → Disables shuffle mode

### 4. **Special Content**
- **News**: `"What's the news"`, `"Tell me the news"`, `"Play the news"`

### 5. **Volume Control** (System-level, affects Spotify output)
- **Relative**: `"Turn volume up"`, `"Turn volume down"`
- **Absolute**: `"Volume 50%"`, `"Set volume to 75"`
- **Extremes**: `"Set volume to max"`, `"Mute"`, `"Set volume to min"`

## Detailed Flow Analysis

### **AI Processing Layer** (`ai_prompt.py` → `ai.py`)
1. **Voice Input**: User speaks command
2. **Transcription**: Whisper API converts speech to text
3. **AI Parsing**: Groq LLM analyzes text and generates JSON response:
   ```json
   {
     "response": "Playing jazz music.",
     "action": "spotify_play",
     "query": "jazz music",
     "type": "playlist"
   }
   ```
4. **Action Dispatch**: Parsed JSON sent to `dispatcher.py`

### **Action Dispatch Layer** (`dispatcher.py`)
The dispatcher routes commands to appropriate handlers:

#### **Spotify Play Flow** (`action: "spotify_play"`)
```python
# Extract parameters
query = parsed.get("query", "")      # "jazz music"
artist = parsed.get("artist", "")      # "AC/DC" (optional)
type = parsed.get("type", "")         # "playlist" (optional)

# Call Spotify handler
success, message = spotify_player.handle_spotify_play(params)
```

#### **Control Commands Flow**
- **Stop**: `spotify_player.stop_playback()`
- **Skip**: `spotify_player.skip_playback()`
- **Repeat**: `spotify_player.repeat_playback(repeat_mode)`
- **Shuffle**: `spotify_player.shuffle_playback(shuffle_bool)`

### **Spotify Engine Layer** (`spotify_app.py`)

#### **Token Management** (Critical for 401 Error Prevention)
1. **Pre-Operation Validation**: Every method calls `initialize_spotify()`
2. **Token Loading**: `load_spotify_token()` checks database
3. **Expiry Check**: Refreshes if token expires within 5 minutes
4. **OAuth Refresh**: Uses `create_spotify_oauth()` with proper redirect_uri
5. **Client Reinitialization**: Creates fresh `spotipy.Spotify()` instance
6. **Verification**: Calls `self.sp.me()` to validate token

#### **Device Management**
1. **Device Discovery**: Searches for "voxMate Pi" device
2. **Memory Cache**: Stores active device ID in memory
3. **Database Cache**: Falls back to cached device ID
4. **Playback Transfer**: Transfers playback to active device
5. **Verification**: Confirms transfer completed within 5 seconds

#### **Content Resolution** (`detect_spotify_type`)
1. **Type Priority**: Uses user-specified type first (track/album/artist/playlist)
2. **Search Strategy**: 
   - **With Artist**: `track:query artist:artist_name`
   - **General**: `query`
3. **Matching Algorithm**:
   - **Exact Match**: Case-insensitive exact string match
   - **Partial Match**: Query contained in item name
   - **Fuzzy Match**: >80% similarity using rapidfuzz
4. **Fallback**: Returns first result if no strong match found

#### **Playback Execution**

**For Albums/Playlists/Artists**:
```python
self.sp.start_playback(
    device_id=device_id,
    context_uri=uri  # spotify:album:ID or spotify:playlist:ID
)
```

**For Individual Tracks**:
```python
# Add to queue
self.sp.add_to_queue(track_uri, device_id=device_id)
# Skip to track if queue exists
if has_queue:
    self.sp.next_track()
# Start playback
self.sp.start_playback(device_id=device_id)
```

**Queue Management**:
- **Existing Queue**: Adds track, then skips to it
- **Empty Queue**: Builds fallback queue with user's top tracks
- **Fallback Playlist**: Uses default playlist if all else fails

#### **Special Content - News**
```python
# Hardcoded news podcast URI
show_uri = "spotify:show:2qZ0xpaBBwf3bTYhA10KZY"

# Get latest episode
episodes = self.sp.show_episodes(show_uri, limit=1)
episode_uri = episodes["items"][0]["uri"]

# Play news episode
self.sp.add_to_queue(uris=[episode_uri])
self.sp.next_track()
self.sp.start_playback(device_id=device_id)
```

### **Main Application Loop** (`main.py`)

#### **Wake Word Detection**
1. **Listening State**: `app_state.set_state("status", "waiting")`
2. **Wake Word**: "Hey Mycroft" triggers processing
3. **Spotify Pause**: Automatically pauses current playback during wake word detection
4. **State Update**: `app_state.set_state("spotify", "paused")`

#### **Command Processing**
1. **Recording**: `AudioProcessor.record_audio_to_file()`
2. **Transcription**: `ai_service.transcribe_audio(audio_file)`
3. **AI Response**: `ai_service.generate_response(transcript)`
4. **Action Execution**: `handle_action(parsed)`
5. **Response Playback**: `ai_service.text_to_speech(response_text)`

#### **Auto-Resume Logic**
After each command completion:
```python
if app_state.is_spotify_paused():
    success, message = handle_action({"action": "spotify_play"})
```

## Error Handling & Recovery

### **Token Expiration (401 Errors)**
1. **Detection**: `_handle_spotify_error()` catches 401 status
2. **Auto-Refresh**: Calls `initialize_spotify()` to refresh token
3. **Retry**: Attempts original operation once with fresh token
4. **Graceful Degradation**: User-friendly error messages if refresh fails

### **Device Management Errors**
- **No Device**: "No valid playback device available"
- **Transfer Failed**: "Failed to transfer playback"
- **Verification Timeout**: "Playback transfer verification timed out"

### **Content Resolution Errors**
- **No Match**: Falls back to user's top tracks
- **Search Failed**: Attempts default playlist
- **Restriction Violations**: Preserves Spotify's native error messages

## State Management

### **Application States** (`app_state`)
- **waiting**: Listening for wake word
- **processing**: Recording/transcribing user command
- **spotify**: playing/stopped/paused

### **Spotify States**
- **playing**: Active playback
- **stopped**: Playback paused/stopped
- **paused**: Temporarily paused (during wake word detection)

## Configuration & Dependencies

### **Required Environment Variables**
- `SPOTIFY_CLIENT_ID`: Spotify application client ID
- `SPOTIFY_CLIENT_SECRET`: Spotify application client secret
- `GROQ_API_KEY`: Groq AI API key
- MongoDB connection for user/token storage

### **Key Components**
- **Spotipy**: Spotify API client library
- **Groq**: AI model for natural language processing
- **Whisper**: Speech-to-text transcription
- **gTTS**: Text-to-speech response
- **MongoDB**: User data and token storage

## Example User Journeys

### **Journey 1: Play Specific Song**
```
User: "Play Bohemian Rhapsody by Queen"
↓
AI: {"response":"Playing Bohemian Rhapsody by Queen.","action":"spotify_play","query":"Bohemian Rhapsody","artist":"Queen","type":"track"}
↓
Spotify: Searches for track → finds exact match → adds to queue → starts playback
↓
Response: "Playing Bohemian Rhapsody by Queen."
```

### **Journey 2: Control Playback**
```
User: "Skip this song"
↓
AI: {"response":"Skipping this song.","action":"spotify_skip"}
↓
Spotify: Validates token → pauses current track → skips to next
↓
Response: "Skipping this song."
```

### **Journey 3: News Playback**
```
User: "What's the news"
↓
AI: {"response":"Getting the news.","action":"news"}
↓
Spotify: Gets latest news podcast episode → adds to queue → plays
↓
Response: "Getting the news."
```

## Performance Optimizations

### **Token Management**
- **Proactive Refresh**: 5-minute expiry buffer prevents 401 errors
- **Singleton Pattern**: Single SpotifyPlayer instance across app
- **Connection Pooling**: Reuses HTTP connections

### **Device Caching**
- **Memory Cache**: Fast device ID lookup
- **Database Cache**: Persistent device storage
- **Active Verification**: Ensures device is actually available

### **Search Optimization**
- **Type Prioritization**: User-specified type searched first
- **Multi-tier Matching**: Exact → Partial → Fuzzy → First result
- **Limited Results**: Searches only 5 items per type for performance

This architecture ensures robust, responsive Spotify control with comprehensive error handling and graceful fallbacks.