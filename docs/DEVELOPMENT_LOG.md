# voxMate Development Log

This document provides a comprehensive, chronological development history for the voxMate project. Entries are in reverse chronological order (newest at top).

---

## November 2025

### 2025-11-25 (Latest Session)
**Branch:** main  
**Commits:** 212965b, e3163d6

- **debug remote/local logic** - Added debugging for remote/local logic handling in main application
- **update remote/local logic** - Updated logic for handling remote vs local operations in voxMate_app/main.py

---

## August 2025

### 2025-08-11 (Thread Management Session)
**Branch:** thread_managment → main  
**Commits:** 5cdd964, 531420a

- **Add remote working function** - Enhanced remote functionality with 16 insertions, 11 deletions in main.py
- **refactor: add type hints to all functions** - Major refactoring across 12 files adding type hints:
  - Updated handlers: news_weather.py, spotify_app.py
  - Updated services: ai.py, audio.py, wakeword.py
  - Updated utils: alsa_suppress.py, mic_lights.py, state.py
  - Updated config and interfaces

### 2025-08-10 (Radio/News Integration)
**Branch:** radio → main  
**Commits:** d596610, fc03b69

- **Remove get_news import from dispatcher** - Cleaned up imports in dispatcher.py
- **Add Spotify news handler** - Major integration adding news functionality:
  - Added audio_thread.py handler (53 lines)
  - Enhanced news_weather.py (65 lines changes)
  - Updated spotify_app.py (59 lines changes)
  - Removed old spotify_app_old.py (583 lines deleted)
  - Updated AI prompt and audio service

### 2025-08-09 (Spotify Testing & Scripts)
**Commits:** fa43b6f, 53d64f7, 9ed5b68

- **Re-test spotify stop** - Extensive refactoring of spotify_app.py (757 lines reorganized)
- **Test Spotify stop** - Added spotify_app_new.py (523 lines) and reorganized spotify handlers
- **Update run and stop scripts** - Enhanced shell scripts:
  - Added comprehensive run_voxMate.sh (47 lines)
  - Added stop_voxMate.sh (25 lines)
  - Removed old script files

### 2025-08-06 (Spotify Service Refactor)
**Commits:** bb25277, 0ca7b6b, 1cac97c, 48fd9bb

- **Refactored Spotify Service, Add spotify news podcast** - Major spotify_app.py refactor (741 lines)
- **Fix typo** - Minor dispatcher.py fix
- **Add news rss feed** - Added RSS feed functionality with 37 insertions across 4 files
- **Update spotify to start at 100% volume** - Simplified volume handling in spotify_app.py

### 2025-08-05 (Volume Control Implementation)
**Commits:** 72cbd2c, f757b02, a58a753

- **Update volume function** - Enhanced volume.py with 23 insertions, 18 deletions
- **Add handling of str and int volume control** - Improved volume control flexibility
- **Add deafult volume to startup and web app** - Major volume integration:
  - Updated volume.py, settings.py, socketio.py, main.py
  - Enhanced web app: users.py, forms.py, models.py, settings.js, settings.html
  - 163 lines added across 9 files

### 2025-08-01 (Volume Limits)
**Commits:** 2c46ecd

- **Add max and min to volume** - Added volume constraints in volume.py and AI prompt

### 2025-07-31 (Spotify Controls & Volume)
**Commits:** 2f3242e, 34dbbd8, 77e05dc, b668ae3, d9cc3b2

- **Add volume control for up, down, value** - Comprehensive volume control system:
  - Added volume.py handler (46 lines)
  - Updated dispatcher, AI prompt, and state management
  - 86 lines added across 5 files
- **mall update to shuffle error handling** - Fixed shuffle error handling
- **Update spotify shuffle** - Enhanced shuffle functionality (28 lines added)
- **Small syntax errors fixed** - Cleaned up AI prompt and main.py
- **Add skip, repeat and shuffle to spotify** - Major spotify control additions:
  - Enhanced spotify_app.py with new controls
  - Updated AI prompt for new commands
  - 39 lines added across 4 files

---

## July 2025

### 2025-07-28 (Spotify & Performance Fixes)
**Commits:** 642f44d, 5759584, 3ff034f, da4d82e

- **Fix wake word spotify stop** - Fixed spotify stopping when wake word detected
- **Fix small errors** - Cleaned up main.py and ai.py
- **Fix performance metrics and remote code** - Performance improvements
- **Add repeat and skip to spotify, add remote working** - Major spotify enhancements:
  - Enhanced dispatcher and spotify_app.py
  - Added remote working functionality
  - Updated AI prompt and main application logic
  - 135 lines added, 100 removed across 6 files

### 2025-07-27 (Audio Cleanup & Mic Lights)
**Commits:** 90746ab, 07942c6, da7147b, 73db72f, 5574b78, 02105ab, 24c8a40, e6a299f, b398928, b4242ab, 9939a10, bf8a191, 327ca11, 05a8129, fadc248, 9d244c9, 68b1922

- **Add mpg123 cleanup check** - Enhanced cleanup.py with better process management
- **Update cleanup output** - Improved cleanup logging
- **Update greeting sound** - Updated greeting.mp3 audio file
- **Cleanup looping sound removal** - Removed looping audio functionality
- **Change mic lights order** - Reorganized mic light processing
- **Remove looping sound** - Major cleanup removing 76 lines across 9 files
- **Update greeting and generating audio** - Updated audio files
- **Remove testing files, completely remove spotify thread imports** - Cleaned up 509 lines
- **Remove spotify thread** - Removed spotify_threads.py (96 lines) and updated dispatcher
- **Add stopp_pulsing to mic lights** - Enhanced mic light functionality
- **Update lights_processing** - Minor mic lights fix
- **Reorder mic lights** - Cleaned up mic light initialization
- **Update ai prompt, mic lights** - Enhanced AI prompts and mic light system
- **Update handling action in main** - Minor main.py update
- **Update action processing in main** - Streamlined action handling
- **Add mic lights scheme** - Major mic light system implementation:
  - Added comprehensive mic light functionality
  - Updated main.py, wakeword.py, and mic_lights.py
  - 60 lines added across 3 files

### 2025-07-25 (Spotify Debug & Queue)
**Commits:** 766d3fb, 336a653, c5f1b15, a98807a, 1f1956e, 4bcd74d, 2a35de1, 3c56399, db90ea3, 81e9cc7, 6a8f5cc, 634516c, 2cb8cb4, 8857dd5, 499b5e2

- **Remove debugging from detect spotify** - Cleaned up spotify debugging
- **add more spotify type debugging** - Added type debugging for spotify
- **Debug user_content_type** - Enhanced content type detection
- **Update spotify detect type** - Improved spotify type detection
- **Update to remote test** - Enhanced remote testing functionality
- **Update handle_spotify and add remote test py** - Added remote_spotify_test.py (32 lines)
- **Simplify handle spotify code** - Streamlined spotify handling
- **Remove thread add track play logic** - Simplified spotify thread management
- **Remove re-add to queue** - Fixed queue management
- **Update typo** - Minor typo fix
- **Add lag time to spotify play** - Added playback lag handling
- **Fix syntax error** - Fixed syntax issues
- **debug add to queue** - Enhanced queue debugging
- **Fix typo in handle_spotify** - Minor typo fix
- **Add Spotify add to queue** - Major queue functionality:
  - Enhanced dispatcher and spotify_app.py
  - 53 lines added across 2 files

### 2025-07-24 (AI Prompts & Mic Lights)
**Commits:** 17fdc02, 395aa65, 8355a7c, 7781f1c, 1c7cdca

- **Update for new ai prompt response** - Enhanced AI response handling
- **Update ai Prompt** - Major AI prompt refactor (52 lines changed)
- **Update ai prompt** - Enhanced AI prompts (32 lines changed)
- **Update Mic Lights cleanup** - Enhanced cleanup for mic lights
- **Update ai prompt, Add mic lights class** - Major mic light system:
  - Added mic_lights.py (76 lines)
  - Added module testing files (500+ lines)
  - Enhanced AI prompts and requirements
  - 622 lines added across 7 files

### 2025-07-21 (AI Prompt Refinements)
**Commits:** 2f26b26, 8649cdb, 2d334c3, f74976f, 0e50afe

- **Update cleanup and ai prompt** - Enhanced cleanup and AI prompts
- **Update ai prompt** - Minor AI prompt update
- **Update ai prompt and success in main** - Enhanced success handling
- **Update ai prompt** - Major AI prompt simplification (86 lines changed)
- **Add improvements to Spotify search** - Enhanced spotify search:
  - Added requirements, enhanced dispatcher and spotify_app.py
  - Major AI prompt updates (58 lines added)
  - 129 lines added across 6 files

### 2025-07-20 (Spotify Thread Management)
**Commits:** 1c0743f, da5b4d6, bc56067, 68f258f, 07bfe29, 68b24ce, 1cb55db, dfbfff5, 582e5ef, 5ee7b2f, cf924c0, 3313749, 77cca3a, a7e59fa, abcc448

- **Correct syntax error** - Fixed spotify_app.py syntax
- **Update detect spotify type to find exact match** - Enhanced type detection
- **Update spotfiy thread** - Minor spotify thread update
- **Update the spotify thread stop** - Enhanced thread stopping
- **add stop to spotify thread immediately** - Improved thread stopping
- **Update spotify thread to add only new tracks** - Enhanced track management
- **Update spotify thread to use artist** - Enhanced artist handling
- **Update web app spotify auth** - Fixed web app authentication
- **Update spotify user scopes** - Enhanced user permissions
- **Update spotify thread** - Major thread refactor (83 lines changed)
- **Add error handling to spotify thread** - Enhanced error handling
- **Update spotify thread** - Thread improvements
- **Update possible syntax error in spotify thread** - Fixed syntax
- **Add fall backs to sportify threads** - Added fallback mechanisms
- **Add Spotify thread to constantly add songs to queue** - Major queue management system

### 2025-07-19 to 2025-07-18 (Audio & Device Management)
**Commits:** c26a531, 28ff311, c8f4396, 417d683, 0d5e296, 0087238, c19bacc, d888c08, a01256d, 2e77bee, 0cce508, b4cbdaf, 0fa782c, 2ff14dd, e1f5bb1, 2d51028, bbb8baf, 90c46a7, 658e69e, 811872c, ba28418, e5ecf5a, 32abffa, 1c6f012, 91406b0, 399c3a6, 7cbf3f7, 8925e5c, 7cd6dfb, 6c61b24, a8acfdd, d98cb2f, dbc698c, b03eab4, 4651d39, b666a4c, b67b893, ba50f31, 61307d7, 51ebf62

- **Change logger to info** - Updated logging levels
- **Add debug to logger** - Enhanced debugging
- **Add debug to detect type and uri in spotify** - Enhanced spotify debugging
- **Small update to spotify** - Minor spotify update
- **Add unsaved files from last commit** - File recovery
- **Update handle Spotify to play radio** - Enhanced radio functionality
- **Update sportify play to add trach uris in a list** - Fixed URI handling
- **Remove input device input index** - Cleaned up device handling
- **Set input device as none** - Device configuration
- **Add debugging to wake word stream** - Enhanced wake word debugging
- **Add missing break to wake word** - Fixed wake word logic
- **Update wake word** - Enhanced wake word detection
- **Remove wait_for_device_release to fix seg error** - Fixed segmentation fault
- **Update mongodb confirmation** - Enhanced MongoDB handling
- **Correct typo in run app script** - Fixed script typo
- **Add app run script** - Added run script
- **Add mic device finder** - Enhanced device detection
- **Improve wake word device detection and sensitivity** - Major wake word improvements
- **Change uri to uris** - Fixed URI handling
- **Update ai prompt** - Enhanced AI prompts
- **Update device index to 2** - Device configuration
- **Update to pulseaudio** - Audio system update
- **Add more aggressive release device** - Enhanced device management
- **Add function to wait for free device** - Device waiting functionality
- **Correct state function calls adding ()** - Fixed function calls
- **Update get_state** - Enhanced state management
- **Add debugging for spotify resume** - Enhanced spotify debugging
- **Update dispatcher logic** - Enhanced dispatching
- **Merged with main for testing** - Merge commit
- **Merge branch 'main' into action_handler to incorporate new mic and speaker setup** - Major merge
- **Update back to 2 channels with wake word conversion** - Audio channel management
- **Update to compensate for system wide 1 channel setting** - Audio configuration
- **Update channels to 1** - Mono audio setup
- **Convert wake word to use 1 channel** - Wake word audio conversion
- **Update device index for new mic** - Device configuration
- **Update channel to 2** - Stereo audio setup
- **Update to use handler for Spotify play** - Enhanced spotify handling
- **Update logger to give more verbose output** - Enhanced logging
- **Update state util to include Spotify playing** - Enhanced state management
- **Add action handler** - Major action system implementation

### 2025-07-17 (File Structure)
**Commits:** 015fd86

- **Change file structure to include action handler** - Major reorganization

### 2025-07-14 (Spotify Integration)
**Commits:** 5fd11a1, 1325195, 6da4b83, e2d2a7b

- **Add appp state to wake word** - Enhanced wake word with app state
- **Update wake word pause spotify** - Enhanced spotify pausing
- **Update ai prompt and simplified it** - AI prompt simplification
- **Update ai prompt to be more explicit** - Enhanced AI prompts

### 2025-07-13 (Spotify & Cleanup)
**Commits:** 9d3764, f73b24f, 9b3274b, a4f5cd3, 66be746, 4c1a737, 48e3bfc, bed2dbd, 22c62a8

- **Fix AudioPlayer circular imports** - Fixed import issues
- **Add more cleanup actions** - Enhanced cleanup
- **Add Spotify stop when wake word detected** - Enhanced wake word integration
- **Add stop_playback before wakeword detection** - Enhanced audio management
- **Update voxSpotify model** - Enhanced spotify models
- **Update voxSpotify data class** - Enhanced data structures
- **Add better logging and correct mongodb handling in Spotify service** - Enhanced logging
- **Add Spotify param control and stop command** - Enhanced spotify controls
- **Tidy up imports** - Code cleanup

### 2025-07-12 (Spotify Structure)
**Commits:** ca13cd4, 8eb921f, 5b298a0

- **Update settings to remove Spotify content** - Cleaned up settings
- **Change spotify_app structure** - Reorganized spotify code
- **Merged all audio changes from audio_change2** - Major audio merge

---

## June 2025

### 2025-07-09 to 2025-06-30 (Audio & Web App)
**Commits:** dd88eec, 0deb70e, 6229846, d5a06c9, 56ed347, ef12071, 8ce35d1, 725268a, 6953682, 2a2b134, 4894a2d, 04a7362, 62462f5, 47ab94f, 9ea3c17, 974417a, df88d9f, bf54ade, 2a79288

- **Remove pulse** - Removed pulseaudio
- **Add playback route to web app** - Enhanced web app
- **Fix small errors, Add debugging** - Bug fixes
- **Add Spotify login to web app** - Major web app enhancement
- **Add debugging, change small errors** - Debugging improvements
- **Add Spotify playback to voxMate app** - Major spotify integration
- **Update git** - Git configuration
- **Change Path local file calls** - File path updates
- **Change local file calls for updated file structure** - Path reorganization
- **Change file structure and removed testing files** - Major reorganization
- **Change keyword path** - Path updates
- **Change load_env call to relative path** - Environment handling
- **Change load_env() location to start of main.py** - Environment loading
- **Move alsa suppress to separate service** - Service separation
- **Add debugging for seg crash** - Crash debugging
- **Debug python env script call** - Environment debugging
- **Update start and stop scripts** - Script enhancements
- **Change voxMate.py to modularised structure** - Major modularization

### 2025-06-29 (Spotify Web App)
**Commits:** b83d2c1, 6eb9877, 57fe877, eaed018, 7fe3530, 56fc199

- **Add code refinements to spotify web app** - Web app refinements
- **Add Spotify login and logout to web app** - Authentication system
- **Commit before adding spotify function to voxMate web app** - Preparation commit
- **Fix typo in start_voxMate.sh** - Script fix
- **Add script to start/stop voxMate** - Management scripts
- **Test spotify API** - API testing

### 2025-06-27 (Device Detection & Volume)
**Commits:** c2fad7d, c8ca84f, 85a4f4c, b2d20a0, 9f65fda, 3ff4699, 5ec4808, fffc229, 8687e35, d1ca4de, 9bddc80, 81e98ed, d68c015, 56ee548, 547ceed, 0314fa0, fda2e01, f270450, 20bb739

- **Add code simplifcation for dection** - Detection simplification
- **Correct error in file update** - File fix
- **Test git push** - Git testing
- **Refine code for ubuntu server** - Server compatibility
- **Refine code for device check with user freindly output** - User experience
- **Add terminal print out for dection** - Enhanced output
- **Add device detection test** - Detection testing
- **Change terminal output for volume_display** - Volume display
- **Correct voulem_duration to voulme_display** - Typo fix
- **Add debugging for volume display** - Volume debugging
- **debug volume display** - Volume fixes
- **Fix web app voulme display bug** - Web app bug fix
- **Change volume_display logging location** - Logging enhancement
- **Add debugging** - General debugging
- **Add debugging** - More debugging
- **Add more logging for voxMate** - Enhanced logging
- **Add logger for volume_display in voxMate** - Volume logging
- **Add volume_display to voxMate** - Volume display feature
- **Add volume_display setting to web app** - Web app volume settings

### 2025-06-26 (Socket.IO & State)
**Commits:** 64f845d, 88d60c0, 88afed1, 32caccb, d3039da, dfc6301, 5ca2ec2, 3b085ce

- **Refine Code in voxMate** - Code refinements
- **Change typo** - Typo fix
- **Add variable for WAKE_WORD in voxMate** - Wake word configuration
- **Add global app_state in voxMate** - State management
- **Commit before big change** - Preparation commit
- **Add extra logging** - Enhanced logging
- **Add to main() in voxMate** - Main function updates
- **Add first socketIO test** - Socket.IO integration

### 2025-06-25 (Porcupine Debugging)
**Commits:** 531a241, 5952af2, b71bd50, ed35e04, cb043cf, f66aaa0, bcb9e0b, 3c0a777, 4974646, 9362303, 1172a30, b184a5e, ea0ecc8, 2804c57

- **Commit ready to merge with main** - Merge preparation
- **Update file location pathh call in voxMate** - Path updates
- **Update snytax error** - Syntax fix
- **Change code order** - Code organization
- **Update dot env loading** - Environment loading
- **Update debug** - Debugging updates
- **Add debug** - Debugging additions
- **Correct typo** - Typo fix
- **Add voxmate debugging** - Application debugging
- **Add more debugging** - Enhanced debugging
- **Update audio file - critical error** - Critical error handling
- **Update warning messages in voxMate** - Warning improvements
- **Update audio files** - Audio updates
- **Update env check in voxMate** - Environment checking

### 2025-06-24 (Database & Configuration)
**Commits:** 36741b8, 4b8887f, af58c36, ae33901, b38267d, 074b36b, be669b3, 47dc459

- **Change file name in web app** - File rename
- **Add host and port config for web app** - Configuration
- **Correct syntax error** - Syntax fix
- **Add db degbug** - Database debugging
- **Add more testing for db config loading** - Database testing
- **Add test for DB config loading** - Database testing
- **Add DEBUG for API key** - API debugging
- **Add testing in voxMAte.py** - Application testing

### 2025-06-23 to 2025-06-18 (Web App & Documentation)
**Commits:** 7e077d8, 3713e48, 75c13c5, e9f7daa, a2de51e, 9360d65, 5387ed1, 19c35cb, b360439, 4b0871b, 7b664f5, 7fe90a1, 0df4c23

- **Add Spotify auth module_testing** - Authentication testing
- **Replace spelling mistake** - Typo fix
- **Add warnings for missing .env vars in web app and voxMate.py. Remove about.html. Add readme.md to index.html** - Environment warnings and UI updates
- **Update readme.md** - Documentation updates
- **Update readme.md** - More documentation
- **Delete file** - File cleanup
- **add porcupine readme.txt** - Documentation addition
- **Remove .ppn from tracking** - Git ignore updates
- **Remove .ppn and LICENSE.txt from tracking** - More git ignore updates
- **Update readme.md and about page** - Documentation and UI
- **Add about page and Update readme.md file** - Documentation and UI
- **Add cookie and T&C web pages** - Legal pages
- **Add settings page to web app** - Settings functionality

### 2025-06-14 (User Authentication)
**Commits:** 0100bd7

- **Add user register, login & logout** - Authentication system

### 2025-06-13 (UI Updates)
**Commits:** ce33b13, 052e0f6, e869b7c, 738c56f

- **change readme.md image size** - UI adjustments
- **change readme.md image size** - More UI adjustments
- **change readme.md image size** - Final UI adjustments
- **Replace node.js with flask, add nav-bar** - Major technology change

### 2025-06-01 (Web GUI Development)
**Commits:** 5fe6577, b3cc0f7, 1f3f008, a6b3019

- **Add web GUI (WIP)** - Web interface development
- **Add file location change** - Path updates
- **Add file location change** - More path updates
- **Add file location change** - Final path updates

---

## Early Development (Before June 2025)

### Core Features Implementation
- **AI API script developed** - Initial AI integration
- **STT Developed** - Speech-to-text functionality
- **pyttsx TTS script developed** - Text-to-speech with pyttsx
- **piper TTS script developed** - Enhanced TTS with Piper
- **gtts TTS script developed** - Google TTS integration
- **Wake word script developed** - Wake word detection
- **Question end detection script developed** - Voice interaction logic
- **Complete voxMate Test developed** - Testing framework
- **voxMate with groq developed** - Groq AI integration
- **voxMate script small adjustments** - Initial refinements
- **Generating audio added** - Audio generation
- **Add looping audio (generating)** - Audio feedback
- **Remove vosk add whisper** - Speech recognition upgrade
- **Add wake word feature and greeting audio** - User interaction
- **Add question end detection** - Enhanced interaction
- **Add python classes to voxMate** - Object-oriented structure
- **Add noise reduction** - Audio quality
- **Add pulseAudio** - Audio system
- **Add file location change** - Path management

---

## Branch Information

### Active Branches
- **main** - Primary development branch
- **radio** - Radio/news functionality (merged to main)
- **thread_managment** - Thread management features (merged to main)

### Merged Features
- **volume_control** - Volume control system
- **spotify_app** - Spotify integration
- **voxMate.py_restructure** - Code modularization
- **spotify_web** - Web app Spotify features
- **audio_device_detection** - Device detection
- **volume_setting** - Volume settings
- **io_socket_test** - Socket.IO integration
- **porcupine_debugging** - Wake word debugging
- **action_handler** - Action system
- **rec_thread** - Recording thread management

---

## Technology Stack Evolution

### Audio Processing
- Started with basic pyttsx TTS
- Evolved to Piper TTS for better quality
- Added noise reduction and pulseaudio support
- Implemented device detection and management

### AI Integration
- Initial AI API integration
- Enhanced with Groq AI
- Continuous prompt refinement for better responses
- Added context awareness and state management

### Web Application
- Started with Node.js
- Migrated to Flask for better Python integration
- Added user authentication, settings, and Spotify integration
- Implemented real-time communication with Socket.IO

### Architecture
- Monolithic voxMate.py script
- Modularized into services, handlers, and utilities
- Added action handler system for extensibility
- Implemented proper state management and cleanup

---

## Key Features Timeline

1. **Basic Voice Assistant** (Early 2025)
   - Speech-to-text and text-to-speech
   - Basic AI responses
   - Wake word detection

2. **Audio Enhancements** (Q2 2025)
   - Better TTS with Piper
   - Noise reduction
   - Device management

3. **Spotify Integration** (Mid 2025)
   - Full Spotify control
   - Queue management
   - Web app authentication

4. **Web Interface** (Mid 2025)
   - Flask-based web app
   - User authentication
   - Settings management
   - Real-time updates

5. **Advanced Features** (Late 2025)
   - News/RSS integration
   - Volume control
   - Mic light feedback
   - Thread management
   - Remote functionality

---

## Development Patterns

### Common Workflows
1. **Feature Development**: Create branch → Develop → Test → Merge to main
2. **Bug Fixes**: Debug in main → Fix → Test → Commit
3. **Refactoring**: Identify improvements → Refactor → Test → Document
4. **Integration**: Add new service → Update handlers → Test integration

### Testing Approach
- Manual testing during development
- Remote testing for Spotify functionality
- Device testing for audio features
- Web app testing for user interface

### Code Quality
- Type hints addition for better maintainability
- Modular structure for extensibility
- Comprehensive logging for debugging
- Cleanup procedures for resource management

---

*Last Updated: 2025-11-25*
*Total Commits Analyzed: 200+*
*Development Period: June 2025 - November 2025*