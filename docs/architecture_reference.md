# voxMate Architecture Reference

## Overview

voxMate is a voice-controlled smart speaker system with two main components:
- **voxMate_app**: Main voice assistant application (Python)
- **voxMate_web_app**: Web interface for configuration and Spotify authentication (Flask)

The system uses wake word detection, AI processing, and Spotify integration to provide a hands-free music and information experience.

---

## 1. Main Entry Points

### voxMate_app/main.py
**Primary entry point for the voice assistant**

**Responsibilities:**
- Initialize all services (AudioProcessor, AIService, MicLights)
- Environment variable validation with audio feedback
- Socket.IO connection to web app for real-time settings updates
- Main execution loop handling wake word detection → recording → AI processing → action execution

**Key Flow:**
```python
main() → initialize_services() → check_environment() → 
connect_socketio() → main_loop() → {
    wake_word_detection() → record_audio() → 
    transcribe_audio() → generate_response() → handle_action()
}
```

### voxMate_web_app/app.py
**Flask web application entry point**

**Responsibilities:**
- Flask app configuration and MongoDB setup
- Blueprint registration for modular routing
- Session management and security configuration
- Environment variable validation for web interface

---

## 2. Service Layer Architecture

### AIService (voxMate_app/services/ai.py)
**Central AI processing service**

**Core Functions:**
- `transcribe_audio()`: Whisper API integration for speech-to-text
- `generate_response()`: Groq API integration with structured JSON output
- `text_to_speech()`: gTTS integration for voice responses

**Dependencies:**
- OpenAI client (Groq API)
- AudioProcessor for playback
- Settings configuration for model selection

### AudioProcessor (voxMate_app/services/audio.py)
**Audio recording and playback service**

**Core Functions:**
- `record_audio_to_file()`: Silence-aware recording with noise reduction
- `play_sound()`: Audio playback with fallback logic

**Features:**
- Configurable noise reduction based on settings
- Volume display for debugging
- Stereo output support with fallback

### WakeWord Service (voxMate_app/services/wakeword.py)
**Porcupine wake word detection**

**Core Functions:**
- `audio_wake_stream()`: Context manager for wake word detection
- `wake_word_detection()`: Continuous listening for wake word

**Integration:**
- Automatically pauses Spotify when wake word detected
- Controls mic lights for visual feedback

---

## 3. Web App ↔ Main App Communication

### Socket.IO Integration
**Real-time settings synchronization**

**Main App (voxMate_app/interfaces/socketio.py):**
- Client connecting to `http://localhost:5000`
- Listens for `settings_updated` events
- Reloads configuration and updates global settings

**Web App (voxMate_web_app/controllers/appSettings.py):**
- Emits `settings_updated` event when settings change
- SocketIO instance injected into appSettings blueprint

### Configuration Flow
```
Web Settings Form → MongoDB Update → Socket.IO Emission → 
Main App Receives → Config Reload → Settings Applied
```

---

## 4. Action Handlers & Dispatcher Pattern

### Dispatcher (voxMate_app/actions/dispatcher.py)
**Central action routing**

**Pattern:**
```python
handle_action(parsed_dict) → Tuple[bool, Optional[str]]
```

**Supported Actions:**
- `spotify_play`: Music playback with query/artist/type parameters
- `spotify_stop/pause`: Playback control
- `spotify_skip`: Track skipping
- `spotify_repeat/shuffle`: Playback modes
- `volume`: System volume control
- `news`: News podcast playback

### Action Handlers

#### SpotifyPlayer (voxMate_app/actions/handlers/spotify_app.py)
**Singleton Spotify integration service**

**Key Features:**
- Device discovery and caching (memory + database)
- Token refresh and validation
- Content type detection (track/album/artist/playlist)
- Fuzzy matching for search queries
- Fallback playback logic

**Architecture:**
- Singleton pattern with thread-safe initialization
- Retry logic for network operations
- Comprehensive error handling with user-friendly messages

#### Volume Handler (voxMate_app/actions/handlers/volume.py)
**System volume control**

**Commands:**
- Relative: "up", "down"
- Absolute: "max", "min", numeric values
- Uses `pactl` for Linux audio control

---

## 5. Configuration & Settings Flow

### Settings Architecture (voxMate_app/config/settings.py)

**Priority Order:**
1. User-specific MongoDB settings
2. Default MongoDB settings  
3. Hardcoded DEFAULT_CONFIG fallbacks

**Configuration Sources:**
- `userConfig/user_config.json`: Local user configuration
- MongoDB `appSettings` collection: User and default settings
- Environment variables: API keys and secrets

**Dynamic Reloading:**
- Socket.IO triggers config reload
- Global module variables updated
- Services use latest settings automatically

### Environment Validation
**Critical vs Warning variables:**
- Critical: GROQ_API_KEY, PORCUPINE_API_KEY, SECRET_KEY, SPOTIFY credentials
- Warning: MONGODB_URI (app can run with defaults)

---

## 6. Audio Processing Pipeline

### Recording Flow
```
Wake Word Detected → Mic Lights (Listening) → 
AudioProcessor.record_audio_to_file() → {
    Silence detection with configurable threshold
    Noise reduction toggle
    Real-time volume monitoring
} → Temporary WAV file
```

### Playback Flow
```
AI Response → gTTS → Temporary MP3 → 
AudioProcessor.play_sound() → mpg123 → PulseAudio
```

### Audio Settings
- Sample Rate: 16kHz
- Channels: 2 (stereo)
- Block Size: 16000
- Configurable silence threshold and duration

---

## 7. AI Service Integration

### Speech-to-Text (Whisper)
**Model:** `whisper-large-v3-turbo` (configurable)
**Language:** English
**Format:** Plain text output

### Text Generation (Groq)
**Model:** `qwen/qwen3-32b` (configurable)
**Prompt Engineering:** Structured JSON output system
**Temperature:** 0.3 (consistent responses)

### Response Processing
```python
AI Response → JSON Cleaning → {
    Parsed successfully? → Extract action + response
    Failed? → Use as plain text response
} → Action execution + TTS
```

### AI Prompt Structure
**System Prompt:** Strict JSON output requirements
**Few-shot Examples:** Comprehensive action examples
**Output Format:** Minified JSON with action/response fields

---

## 8. State Management

### AppState (voxMate_app/utils/state.py)
**Thread-safe application state**

**State Keys:**
- `status`: "waiting", "processing", etc.
- `spotify`: "playing", "paused", "stopped"
- `volume`: Current volume level (0-100)
- `alarm`: Future alarm states

**Thread Safety:**
- Lock-based synchronization
- Atomic state updates with logging

### State Usage Patterns
```python
# Check state
if app_state.is_spotify_playing():
    handle_action({"action": "spotify_stop"})

# Update state  
app_state.set_state("spotify", "paused")
```

---

## 9. Database Schema

### MongoDB Collections

#### appSettings
```javascript
{
  user_id: "user123" | "default",
  silence_threshold: 14200,
  silence_duration: 1.0,
  volume_display: false,
  noise_reduction: true,
  stt_model: "whisper-large-v3-turbo",
  ai_model: "qwen/qwen3-32b",
  default_volume: 70
}
```

#### voxSpotify
```javascript
{
  user_id: "user123",
  token_info: {
    access_token: "...",
    refresh_token: "...",
    expires_at: timestamp
  },
  device_id: "b16c033229c6e42b50fcc84989e90f4fc0be26c0",
  last_updated: ISODate,
  user_code: "auth_code_temp"
}
```

#### users
```javascript
{
  user_id: "user123",
  api_token: "state_token",
  // Other user fields
}
```

---

## 10. Error Handling Patterns

### Service Layer
**Consistent Tuple Returns:** `(success: bool, message: str)`
**Logging:** Structured error logging with context
**Graceful Degradation:** Fallback options for critical failures

### Spotify Integration
**Error Categories:**
- Permission errors (403)
- Resource not found (404)
- Restriction violations (Spotify-specific)
- Network timeouts (retry logic)

### Audio Processing
**Critical Errors:** Raised to main loop for handling
**Non-critical Errors:** Logged but don't stop execution
**Cleanup:** Temporary file removal in finally blocks

---

## 11. Security Considerations

### Environment Variables
**All secrets in .env file:**
- API keys (Groq, Porcupine, Spotify)
- Database URIs
- Secret keys for sessions

### Web Security
**Flask Session Configuration:**
- HTTPOnly cookies
- Secure flag in production
- SameSite Lax protection
- Signed sessions with refresh

### Token Management
**Spotify OAuth:**
- State token validation
- Automatic token refresh
- Secure token storage in MongoDB

---

## 12. Hardware Integration

### Microphone Control
**Wake Word:** PyAudio with Porcupine
**Recording:** sounddevice library
**Visual Feedback:** LED control through MicLights

### Audio Output
**Playback:** mpg123 with PulseAudio
**Volume Control:** pactl command-line interface
**Device Management:** Automatic device detection

### LED Feedback
**States:**
- Idle: Breathing effect
- Wake Word Detected: Flash
- Listening: Solid color
- Processing: Pulsing effect

---

## 13. Development & Deployment

### File Structure
```
voxMate/
├── voxMate_app/           # Main voice assistant
│   ├── actions/           # Command handlers
│   ├── config/            # Configuration management
│   ├── interfaces/       # External integrations
│   ├── models/            # Data models
│   ├── services/          # Core services
│   └── utils/             # Utilities
├── voxMate_web_app/       # Web interface
│   ├── controllers/       # Route handlers
│   ├── models/            # Web models/forms
│   ├── static/            # CSS/JS/images
│   └── templates/         # HTML templates
└── userConfig/            # Local user settings
```

### Dependencies
**Core Services:**
- `openai`: Groq API client
- `pvporcupine`: Wake word detection
- `spotipy`: Spotify integration
- `flask-socketio`: Real-time communication
- `pymongo`: Database connectivity

### Configuration Management
**Environment-based:**
- `.env` file for secrets
- Dynamic settings via web interface
- Runtime configuration updates

---

## 14. Flow Summary

### Complete Voice Command Flow
```
1. Wake Word Detection ("Hey VoxMate")
   ↓
2. Spotify Auto-pause (if playing)
   ↓
3. Visual Feedback (LEDs)
   ↓
4. Audio Recording (silence-aware)
   ↓
5. Speech-to-Text (Whisper)
   ↓
6. AI Processing (Groq + structured prompt)
   ↓
7. Action Extraction (JSON parsing)
   ↓
8. Command Execution (dispatcher)
   ↓
9. Response Generation (TTS)
   ↓
10. Audio Playback + State Updates
```

### Settings Update Flow
```
1. Web Form Submission
   ↓
2. MongoDB Update
   ↓
3. Socket.IO Emission
   ↓
4. Main App Receives
   ↓
5. Config Reload
   ↓
6. Service Updates
```

This architecture provides a robust, scalable foundation for a voice-controlled smart speaker with real-time configuration updates and comprehensive error handling.