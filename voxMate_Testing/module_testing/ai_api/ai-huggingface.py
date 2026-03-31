# Script runs and expects a user input. 
# Type a question to as the ai api and it should give back an answer in text.

from huggingface_hub import InferenceClient
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../../.env")

client = InferenceClient(
    provider="together",
    api_key=os.getenv("HUGGINGFACE_HUB"),
)

def query(prompt):
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    message = completion.choices[0].message.content

    # Remove <think>...</think> content if present
    message = re.sub(r"<think>.*?</think>", "", message, flags=re.DOTALL).strip()
    return message

# PROMPT = """In a short answer, ideal for output on a smart speaker can you answer the following; what's the capital of France"""

print("What do you want to ask?")
PROMPT = input()
print(query(PROMPT))