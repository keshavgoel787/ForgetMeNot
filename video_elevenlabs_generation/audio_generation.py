import requests
import asyncio

url = "https://forgetmenot-eq7i.onrender.com/text-to-speech"

headers = {"Content-Type": "application/json"}


async def get_audio():
    data = {
    "text": "nice time to fly, huh?",
    "name": "therapist"
    }

    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Audio saved as output.mp3")
        return "Success"
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return "Error"

async def generate_video():
    audio = asyncio.create_task(get_audio())

    while not audio.done():
        print("Playing sitting still video") # some visual feedback
        await asyncio.sleep(0.1)  # to not overflow terminal

    result = await audio  # get result when done
    print("Result:", result)

asyncio.run(generate_video())
