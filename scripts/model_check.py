import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ GEMINI_API_KEY not found in environment")
    exit(1)

# List models using REST API
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    models = response.json().get('models', [])
    print("Available Gemini models:\n")
    for model in models:
        if 'generateContent' in model.get('supportedGenerationMethods', []):
            print(f"  • {model['name']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
