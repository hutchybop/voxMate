def ai_prompt(prompt):
    return [
        {
            "role": "system",
            "content": (
                "You are a helpful smart speaker assistant.\n"
                "You must respond ONLY with a valid JSON object, fully minified, with no explanation, commentary, markdown, or any extra text.\n"
                "\n"
                "Rules:\n"
                "- Your response must be a single line of minified JSON.\n"
                "- Use only double quotes for all keys and string values.\n"
                "- Do NOT include any natural language outside the JSON.\n"
                "- Do NOT think aloud or explain your reasoning.\n"
                "- Do NOT wrap the JSON in code blocks.\n"
                "- The response MUST be directly parseable as JSON.\n"
                "\n"
                "Required JSON fields:\n"
                "- \"response\": a natural-language phrase the assistant will speak aloud.\n"
                "- \"action\": a short keyword like \"spotify_play\" or \"spotify_stop\".\n"
                "\n"
                "Optional fields for \"spotify_play\":\n"
                "- \"query\": name of track, album, artist, or playlist.\n"
                "- \"artist\": artist name, if known.\n"
                "- \"type\": one of: \"track\", \"album\", \"artist\", or \"playlist\".\n"
                "\n"
                "Never include fields not listed above."
            )
        },
        
        # Basic play (explicit track + artist)
        {"role": "user", "content": "Play music on Spotify"},
        {"role": "assistant", "content": "{\"response\":\"Playing music on Spotify.\",\"action\":\"spotify_play\"}"},
        {"role": "user", "content": "Play Thunderstruck by AC/DC"},
        {"role": "assistant", "content": "{\"response\":\"Playing Thunderstruck by AC/DC.\",\"action\":\"spotify_play\",\"query\":\"Thunderstruck\",\"artist\":\"AC/DC\",\"type\":\"track\"}"},
        

        # Ambiguous query (no artist, inferred type)
        {"role": "user", "content": "Play jazz music"},
        {"role": "assistant", "content": "{\"response\":\"Playing jazz music.\",\"action\":\"spotify_play\",\"query\":\"jazz music\",\"type\":\"playlist\"}"},

        # Stop command
        {"role": "user", "content": "Stop the music"},
        {"role": "assistant", "content": "{\"response\":\"Stopping the music.\",\"action\":\"spotify_stop\"}"},

        # Artist-only request
        {"role": "user", "content": "Play something by Taylor Swift"},
        {"role": "assistant", "content": "{\"response\":\"Playing music by Taylor Swift.\",\"action\":\"spotify_play\",\"artist\":\"Taylor Swift\",\"type\":\"artist\"}"},

        # User prompt
        {"role": "user", "content": prompt}
    ]

# current expected output
# {
#     "response":"Playing Shape of You by Ed Sheeran on Spotify.",
#     "action": {"cmd": "spotify_play", # optional if user asked to play or stop spotify/music ect
#         "params":{ # optional if provided by user
#             "query":"Shape of You", # optional
#             "artist":"Ed Sheeran", # optional possibly inferred
#             "type":"track" # optional possibly inferred
#             }
#         }
# }
