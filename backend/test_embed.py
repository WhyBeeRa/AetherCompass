import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("API key missing")
    exit(1)

# Testing the v1beta endpoint which has text-embedding-004
url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"

payload = {
    "model": "models/text-embedding-004",
    "content": {
        "parts": [{"text": "Hello world"}]
    }
}

headers = {"Content-Type": "application/json"}

print(f"Testing {url}...")
response = requests.post(url, json=payload, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
