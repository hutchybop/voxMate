from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv("../../.env")
key = os.getenv("OPEN_API_KEY")

question = "What is the most common dog name in the uk?"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)


response = client.chat.completions.create(
    model="mistral-saba-24b",
    messages=[
        {"role": "system", "content": "You are to give short concise answers to questions."},
        {"role": "user", "content": question}
    ]
)
print(response.choices[0].message.content)
