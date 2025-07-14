def ai_prompt(prompt):
    return [
        {
            "role": "system",
            "content": (
                "Respond ONLY with valid JSON using this exact format:\n"
                "{\n"
                "  \"response\": \"string\",\n"
                "  \"action\": \"optional_action_name\",\n"
                "  \"params\": \"optional_parameters\"\n"
                "}\n\n"
                
                "Rules:\n"
                "1. The entire response must be valid JSON\n"
                "2. Only include the JSON object, nothing else\n"
                "3. Keep responses short and conversational\n"
                "4. If unsure, omit action and params\n\n"
                
                "Action Reference:\n"
                "- spotify_play: Play music (params: song/artist name)\n"
                "- spotify_stop: Stop playback\n"
                "- set_timer: Set timer (params: duration)\n"
                "- set_alarm: Set alarm (params: time)\n\n"
                
                "Examples:\n"
                "User: Play jazz music\n"
                "{\"response\": \"Playing jazz music\", \"action\": \"spotify_play\", \"params\": \"jazz\"}\n"
                "User: Stop\n"
                "{\"response\": \"Stopping playback\", \"action\": \"spotify_stop\"}\n"
                "User: Hello\n"
                "{\"response\": \"Hi there!\"}\n\n"
                
                "Now respond to:\n" + prompt
            )
        }
    ]