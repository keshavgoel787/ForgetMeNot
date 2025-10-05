import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

data = {
    "contents": [{
        "parts": [{"text": "Say hello in one word"}]
    }]
}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    text = result['candidates'][0]['content']['parts'][0]['text']
    print(f"✓ Gemini 2.5-flash works: {text}")
else:
    print(f"✗ Error {response.status_code}: {response.text}")
