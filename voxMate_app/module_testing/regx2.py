import re
from typing import Dict, Optional

CORE_PATTERNS = {
    "play_music": [
        r"^play$",                         # "play"
        r"^play (?:music|spotify)$",        # "play music"
        r"^play (song|track) (.+)$",        # "play song Yesterday"
        r"^play album (.+)$",               # "play album Thriller"
        r"^play (.+) by (.+)$"              # "play Happy by Pharrell"
    ],
    "stop_music": [
        r"^(stop|pause|halt)$",
        r"^(stop|pause) (?:the )?music$"
    ]
}

def clean_query(text: str) -> str:
    """Remove common filler words"""
    removals = ["the", "song", "track", "album", "please", "could you"]
    words = text.split()
    return " ".join(w for w in words if w not in removals)

def match_intent(text: str) -> Optional[Dict]:
    text = text.strip().lower()
    
    # First try core patterns
    for intent, patterns in CORE_PATTERNS.items():
        for pattern in patterns:
            match = re.fullmatch(pattern, text)
            if match:
                groups = match.groups()
                params = {}
                
                if intent == "play_music":
                    if not groups:
                        return {"action": {"cmd": intent, "params": {}}, "confidence": 1.0}
                    
                    if len(groups) == 2:  # "X by Y" pattern
                        return {
                            "action": {
                                "cmd": intent,
                                "params": {
                                    "query": clean_query(groups[0]),
                                    "artist": groups[1],
                                    "type": "track"
                                }
                            },
                            "confidence": 1.0
                        }
                    else:  # Simple play type
                        return {
                            "action": {
                                "cmd": intent,
                                "params": {
                                    "query": clean_query(groups[1] if len(groups)>1 else groups[0]),
                                    "type": groups[0] if len(groups)>1 else None
                                }
                            },
                            "confidence": 1.0
                        }
                else:  # stop commands
                    return {"action": {"cmd": intent, "params": {}}, "confidence": 1.0}
    
    # Everything else goes to NLU
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