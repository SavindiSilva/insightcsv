import os

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("ANTHROPIC_API_KEY is not set.")

client = Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": "Explain in one sentence what data analysis is."
        }
    ]
)

for block in message.content:
    if block.type == "text":
        print(block.text)