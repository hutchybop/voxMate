import re
from typing import Dict, Optional

# INTENT_PATTERNS = {
#     "play_music": [
#         # 1. Most specific patterns (multiple constraints)
#         r"\bplay(?: the)? song (?P<track>.+?) (?:from|off) (?:the )?album (?P<album>.+?) by (?P<artist>.+?)(?: on spotify)?\b",
#         r"\bplay (?:the )?(?P<track>.+?) by (?P<artist>.+?) from (?:the )?album (?P<album>.+?)(?: on spotify)?\b",
#         r"\bplay (?:latest|newest|recent) (?:album|release) by (?P<artist>.+?)(?: on spotify)?\b",
#         r"\bplay (?P<dynamic_query>top|popular|latest) (?P<dynamic_type>songs|tracks|album) by (?P<artist>.+?)(?: on spotify)?\b",
        
#         # 2. Artist + album/track combos (with optional "on Spotify")
#         r"\bplay (?:the )?album (?P<album>.+?) by (?P<artist>.+?)(?: on spotify)?\b",
#         r"\bplay (?:the )?song (?P<track>.+?) by (?P<artist>.+?)(?: on spotify)?\b",
#         r"\bplay (?P<track>.+?) by (?P<artist>.+?)(?: on spotify)?\b",
        
#         # 3. Playlist/radio requests (with better "my" handling)
#         r"\bplay (?:my )?(?P<playlist>.+? (?:radio|station))(?: on spotify)?\b",
#         r"\bplay (?:my )?(?P<playlist>.+?) playlist(?: on spotify)?\b",
#         r"\bplay (?:my )?(?P<playlist>saved|liked|favorites|favourite)(?: (?:songs|tracks))?(?: on spotify)?\b",
#         r"\bplay (?:my )?(?P<playlist>.+?)(?: on spotify)?\b",
        
#         # 4. Artist-only requests
#         r"\bplay (?:songs|music|tracks|albums) by (?P<artist>.+?)(?: on spotify)?\b",
#         r"\bplay (?:artist|band) (?P<artist>.+?)(?: on spotify)?\b",
        
#         # 5. Standalone album/track requests
#         r"\bplay (?:the )?album (?P<album>.+?)(?: on spotify)?\b",
#         r"\bplay (?:the )?song (?P<track>.+?)(?: on spotify)?\b",
        
#         # 6. Contextual requests
#         r"\bplay (?:some|more|similar|related)(?: music| songs)?(?: on spotify)?\b",
        
#         # 7. Fallback (catch-all)
#         r"\bplay (?P<name>.+?)(?: on spotify)?\b",
#     ],
#     "stop_music": [
#         r"\bstop(?:\s*(?:the|this|that|it))?\b",
#         r"\bpause(?:\s*(?:the|this|that|it))?\b",
#         r"\bstop (?:the )?music\b",
#         r"\bhalt(?:\s*(?:the|this|that|it))?\b",
#         r"\bshut (?:the|this|that|it) (?:music )?(?:down|off)?\b",
#     ]
# }

# # Words that shouldn't be used as query on their own
# GENERIC_TERMS = {"something", "some music", "spotify", "music", "a song", "a track", "some", "songs", "radio", "station", "some", "more", "similar", "related"}

# def match_intent(text: str) -> Optional[Dict]:
#     text = text.strip().lower()
    
#     # Remove "on spotify" mentions as they don't affect the query
#     cleaned_text = re.sub(r'\bon spotify\b', '', text).strip()

#     # Early check for artist names that include "radio" (e.g., "Radiohead")
#     artist_match = re.search(r"\bplay (?P<artist>radio\s*\w+)", cleaned_text)
#     if artist_match and not any(term in cleaned_text for term in [" radio", " station"]):
#         artist = artist_match.group("artist").strip()
#         return {
#             "action": {
#                 "cmd": "play_music",
#                 "params": {"query": artist, "type": "artist"}
#             },
#             "confidence": 1.0
#         }

#     # Handle radio/station requests (only if "radio" or "station" appears as separate words)
#     if " radio" in cleaned_text or " station" in cleaned_text:
#         query = re.sub(r"\b(?:radio|station)\b", "", cleaned_text).replace("play", "").strip()
#         if query.startswith("my "):
#             query = query[3:]
#         return {
#             "action": {
#                 "cmd": "play_music",
#                 "params": {"query": query, "type": "playlist"}
#             },
#             "confidence": 1.0
#         }

#     for intent, patterns in INTENT_PATTERNS.items():
#         for pattern in patterns:
#             match = re.search(pattern, cleaned_text)
#             if match:
#                 groups = {k: v.strip() for k, v in match.groupdict().items() if v}
#                 query = ""
#                 artist = ""
#                 media_type = ""

#                 if "track" in groups and "artist" in groups:
#                     query = groups["track"]
#                     artist = groups["artist"]
#                     media_type = "track"
#                 elif "track" in groups:
#                     query = groups["track"]
#                     media_type = "track"
#                 elif "album" in groups and "artist" in groups:
#                     query = groups["album"]
#                     artist = groups["artist"]
#                     media_type = "album"
#                 elif "album" in groups:
#                     query = groups["album"]
#                     media_type = "album"
#                 elif "playlist" in groups:
#                     query = groups["playlist"]
#                     if query.startswith("my "):
#                         query = query[3:]
#                     media_type = "playlist"
#                 elif "artist" in groups:
#                     query = groups["artist"]
#                     artist = groups["artist"]
#                     media_type = "artist"
#                 elif "name" in groups:
#                     query = groups["name"]
#                     if query in GENERIC_TERMS:
#                         return {
#                             "action": {
#                                 "cmd": intent,
#                                 "params": {}
#                             },
#                             "confidence": 1.0
#                         }
#                     media_type = "artist" if len(query.split()) == 1 else "track"
#                 elif any(term in cleaned_text for term in GENERIC_TERMS):
#                     return {
#                         "action": {
#                             "cmd": intent,
#                             "params": {}
#                         },
#                         "confidence": 1.0
#                     }

#                 return {
#                     "action": {
#                         "cmd": intent,
#                         "params": {
#                             "query": query,
#                             "artist": artist,
#                             "type": media_type
#                         }
#                     },
#                     "confidence": 1.0
#                 }

#     return None

INTENT_PATTERNS = {
    "play_music": [
        # Basic commands (high reliability)
        r"^play (?:spotify|music|some music)$",
        r"^play (?:track|song) (.+)$",
        r"^play (?:album) (.+)$",
        r"^play (?:playlist) (.+)$",
        r"^play (.+) by (.+)$",  # Simple artist-track pairing
    ],
    "stop_music": [
        r"^(?:stop|pause|halt)$",
        r"^(?:stop|pause) (?:the )?music$"
    ]
}

def match_intent(text: str) -> Optional[Dict]:
    text = text.strip().lower()
    
    # Handle basic play commands
    if re.match(r"^play (?:spotify|music|some music)$", text):
        return {
            "action": {"cmd": "play_music", "params": {}},
            "confidence": 1.0
        }
    
    # Handle play [track] by [artist]
    artist_track = re.match(r"^play (.+?) by (.+)$", text)
    if artist_track:
        return {
            "action": {
                "cmd": "play_music",
                "params": {
                    "query": artist_track.group(1),
                    "artist": artist_track.group(2),
                    "type": "track"
                }
            },
            "confidence": 1.0
        }
    
    # Handle other simple patterns
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                groups = match.groups()
                params = {}
                
                if intent == "play_music":
                    if groups:
                        params = {"query": groups[0], "type": pattern.split()[1]}
                
                return {
                    "action": {"cmd": intent, "params": params},
                    "confidence": 1.0
                }
    
    # Fallback to NLU system
    return None



### Testing
test_commands = [
    # "Play Born in the USA by Bruce Springsteen",
    # "Play the album 1989 by Taylor Swift",
    # "Play Thunderstruck by AC/DC",
    # "Play the song Yellow",
    # "Play songs by Eminem",
    # "Play the album Rumours",
    # "Play the song One Dance by Drake",
    # "Play Back in Black",
    # "Play chilled vibes playlist",
    # "Play my 90s mix",
    # "Play Adele",
    # "Play some music",
    # "Stop the music",
    # "Pause",
    # "Play something by Queen",
    # "Play the song Blinding Lights from the album After Hours by The Weeknd",
    # "Shut the music down"
    # "Play Hotel California by Eagles",
    # "Play the song C.R.E.A.M. by Wu-Tang Clan",
    # "Play latest album by Arctic Monkeys",
    # "Could you play Imagine by John Lennon?",
    # "Play Sicko Mode by Travis Scott feat. Drake",
    # "Play Queen live at Wembley",
    # "Play 80s rock radio",
    # "Pause the music",
    # "Stop playback",
    # "What's the weather today?",

    # Specific track requests
    "play the song Bohemian Rhapsody from the album A Night at the Opera by Queen",
    "play song Yesterday by The Beatles",
    "play Stairway to Heaven by Led Zeppelin",
    "play the song Blinding Lights by The Weeknd",
    
    # Album requests
    "play the album Thriller by Michael Jackson",
    "play latest album by Taylor Swift",
    "play the album After Hours",
    "play newest release by Drake",
    
    # Artist requests
    "play songs by Coldplay",
    "play music by Ed Sheeran",
    "play artist Radiohead",
    "play band Arctic Monkeys",
    
    # Playlist/radio requests
    "play workout playlist",
    "play my running playlist",
    "play 80s rock radio",
    "play jazz station",
    "play my liked songs",
    "play my favorites",
    "play saved tracks",
    
    # Dynamic queries
    "play top songs by Kendrick Lamar",
    "play popular tracks by Billie Eilish",
    "play latest album by Adele",
    
    # Contextual requests
    "play similar music",
    "play more songs like this",
    "play some music",
    
    # Spotify-specific requests
    "play Discover Weekly on Spotify",
    "play my Daily Mix 1",
    "play Release Radar",
    
    # Edge cases
    "play radio edit",
    "play radio gaga by queen",
    "play station to station by david bowie",
    "play my radiohead playlist",
    
    # Stop commands
    "stop",
    "stop the music",
    "pause",
    "halt",
    "shut the music down",
    
    # Natural language variations
    "could you play happy by pharrell williams",
    "please play the album dark side of the moon",
    "I'd like to hear some classical music",
    "put on some jazz",
    
    # Generic requests
    "play something",
    "play some music",
    "play a song",
    
    # Potential false positives
    "play the game",
    "play station",
    "play radio",
    "play something by the way"
]

def test_intent_matching():
    for command in test_commands:
        result = match_intent(command)
        print(f"Input: {command}")
        print("Output:", result, "\n")

# Call the test
test_intent_matching()