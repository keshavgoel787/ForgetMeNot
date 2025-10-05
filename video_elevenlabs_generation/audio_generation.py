import requests
import asyncio

url = "https://forgetmenot-eq7i.onrender.com/text-to-speech"

headers = {"Content-Type": "application/json"}


async def get_audio(data: dict = {"text": "nice time to fly, huh?","name": "Tyler"}):
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Audio saved as output.mp3")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

async def play_talking_video():
    print("Playing talking video") # some visual feedback
    await asyncio.sleep(2.5)  # simulate talking
    return "✅ done talking"

async def generate_video():
    audio = asyncio.create_task(get_audio())

    while not audio.done():
        print("Playing sitting still video") # some visual feedback
        await asyncio.sleep(0.2)  # to not overflow terminal

    result = await audio  # get result when done

    if result:
        print(await play_talking_video())

asyncio.run(generate_video())
