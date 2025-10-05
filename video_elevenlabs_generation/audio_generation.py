import requests
import asyncio
from mutagen.mp3 import MP3

url = "https://forgetmenot-eq7i.onrender.com/text-to-speech"

headers = {"Content-Type": "application/json"}

# replace all "some visual feedback" comments
# currently just placeholder
data = {"text": "Can you try to remember me?","name": "Tyler"}


async def get_audio(data: dict):
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Audio saved as output.mp3")
        return MP3("output.mp3").info.length
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return 0

async def play_talking_video(name, length = 1):
    print(f"{name}_talking.mp4") # some visual feedback
    await asyncio.sleep(length)
    return "✅ done talking"

async def generate_video(data: dict):
    audio = asyncio.create_task(get_audio(data))

    while not audio.done():
        print("{data["name"]}_talking.mp4") # some visual feedback
        await asyncio.sleep(0.2)

    result = await audio

    if result != 0:
        print(await play_talking_video(data["name"], result))
    print("data["name"]_silent.mp4") # some visual feedback

asyncio.run(generate_video(data))
