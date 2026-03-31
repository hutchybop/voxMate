from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re

load_dotenv("../../.env")
key = os.getenv("OPEN_API_KEY")

prompt = "what is the captial of france"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)


response = client.chat.completions.create(
    model="mistral-saba-24b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a helpful smart speaker assistant. "
                "Always respond with a JSON object containing:\n"
                "- 'response': a short sentence suitable for speech.\n"
                "If the user asks to play music (even vaguely, e.g. 'play music', 'play Spotify', 'play'), include:\n"
                "- 'action': 'spotify_play'\n"
                "- 'params': a string with the name of a song, artist, or playlist. "
                "Leave it empty ('') if nothing specific is mentioned.\n"
                "\nExamples:\n"
                "User: Play Bohemian Rhapsody\n"
                "{\"response\": \"Playing Bohemian Rhapsody from Spotify.\", \"action\": \"spotify_play\", \"params\": \"Bohemian Rhapsody\"}\n"
                "User: Play music\n"
                "{\"response\": \"Playing music from Spotify.\", \"action\": \"spotify_play\", \"params\": \"\"}\n"
                "User: What's the time?\n"
                "{\"response\": \"It's 8:15 PM.\"}\n"
                "Respond only with a JSON object like above."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    max_tokens=100,
    temperature=0.7
)


raw_content = response.choices[0].message.content.strip()

# Remove <think> tags and markdown code blocks
cleaned = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL)
cleaned = re.sub(r"^```(?:json)?\s*|```$", "", cleaned, flags=re.MULTILINE).strip()

try:
    parsed = json.loads(cleaned)
    response_text = parsed.get("response", "Sorry, I didn't understand that.")
    action = parsed.get("action")
    param_string = parsed.get("params", "")

    if action == "spotify_play":
        print("Response:", response_text)
        print("Action:", action)
        print("Params:", param_string)  # string, e.g. "Pink"
    else:
        print("Response:", response_text)

except json.JSONDecodeError:
    print("Response (not valid JSON):", raw_content)