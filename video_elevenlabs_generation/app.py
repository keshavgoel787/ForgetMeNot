import requests
import sys

url = "https://forgetmenot-eq7i.onrender.com/text-to-speech"

data = {
    "text": "nice time to fly, huh?",
    "name": "Tyler"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)

# Check if the request succeeded
if response.status_code == 200:
    # Save the returned audio file
    with open("output.mp3", "wb") as f:
        f.write(response.content)
    print("✅ Audio saved as output.mp3")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
