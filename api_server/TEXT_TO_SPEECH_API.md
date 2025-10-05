# Text-to-Speech API

Generate speech in anyone's voice using their voice clone.

## Endpoint

```
POST /text-to-speech
```

## Request

**Content-Type:** `application/json`

```json
{
  "text": "Hi, how are you?",
  "name": "Hannah"
}
```

**Fields:**
- `text` (string, required): The text to convert to speech
- `name` (string, required): Name of the person (case-insensitive)

## Response

**Content-Type:** `audio/mpeg`

Returns an MP3 file with the generated speech.

## Example Usage

### cURL

```bash
curl -X POST http://localhost:8000/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{"text": "Hi, how are you?", "name": "Hannah"}' \
  --output hannah_speech.mp3
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/text-to-speech"
data = {
    "text": "Hi, how are you?",
    "name": "Hannah"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    with open("hannah_speech.mp3", "wb") as f:
        f.write(response.content)
    print("✅ Speech generated!")
else:
    print(f"❌ Error: {response.json()}")
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:8000/text-to-speech', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'Hi, how are you?',
    name: 'Hannah'
  })
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'hannah_speech.mp3';
  a.click();
});
```

## List Available Voices

### Endpoint

```
GET /voices
```

### Response

```json
{
  "voices": ["tyler", "hannah", "steve", "avery", "spot"],
  "count": 5
}
```

### Example

```bash
curl http://localhost:8000/voices
```

```python
import requests

response = requests.get("http://localhost:8000/voices")
voices = response.json()

print(f"Available voices: {', '.join(voices['voices'])}")
```

## Error Responses

### Voice Not Found

**Status:** `404 Not Found`

```json
{
  "detail": "Voice not found for 'InvalidName'. Available: tyler, hannah, steve, avery, spot"
}
```

### API Key Not Configured

**Status:** `500 Internal Server Error`

```json
{
  "detail": "ELEVENLABS_API_KEY not configured"
}
```

### ElevenLabs API Error

**Status:** `4xx` or `500`

```json
{
  "detail": "ElevenLabs API error: <error message>"
}
```

## Configuration

The server requires `ELEVENLABS_API_KEY` in the `.env` file:

```bash
ELEVENLABS_API_KEY=your_api_key_here
```

## Voice Clones

The API automatically discovers voice clones from ElevenLabs that end with `_voice_forgetmenot`:

- `Tyler_voice_forgetmenot` → Available as `"tyler"`
- `Hannah_voice_forgetmenot` → Available as `"hannah"`
- `Steve_voice_forgetmenot` → Available as `"steve"`

Voice clones must be created first using the `upload_voices_to_elevenlabs.py` script.

## Interactive API Documentation

Start the server and visit:

```
http://localhost:8000/docs
```

This provides an interactive Swagger UI where you can:
- Test the endpoints
- See request/response schemas
- Try different inputs

## Notes

- Voice names are case-insensitive (`"Hannah"`, `"hannah"`, `"HANNAH"` all work)
- Generated audio is MP3 format
- Quality depends on the source voice samples
- Each request costs ElevenLabs API credits

## Tips

### Best Text for Speech

- ✅ **Clear sentences**: "Hi, how are you doing today?"
- ✅ **Natural language**: "Hey! Great to see you."
- ❌ **Avoid special characters**: `<script>`, `[brackets]`
- ❌ **Keep it reasonable**: Very long text may timeout

### Voice Quality

The generated speech quality depends on:
1. **Source audio quality**: Clear, noise-free recordings
2. **Audio length**: More audio = better clone (30+ seconds recommended)
3. **Speaker consistency**: Same environment, same tone

## Troubleshooting

### "Could not load ElevenLabs voices"

**Problem:** API key not configured or invalid

**Solution:**
```bash
# Add to .env file
ELEVENLABS_API_KEY=your_actual_api_key
```

### "Voice not found for 'name'"

**Problem:** Voice clone doesn't exist in ElevenLabs

**Solution:**
1. Check available voices: `GET /voices`
2. Upload voice clone: `python upload_voices_to_elevenlabs.py`
3. Verify name matches (case-insensitive)

### Empty or corrupted MP3

**Problem:** ElevenLabs API error or network issue

**Solution:**
- Check API key is valid
- Verify you have ElevenLabs credits
- Check internet connection
- Try shorter text

## Advanced Usage

### Batch Generation

```python
import requests

people = ["Tyler", "Hannah", "Steve"]
text = "Hey! How's it going?"

for person in people:
    response = requests.post(
        "http://localhost:8000/text-to-speech",
        json={"text": text, "name": person}
    )
    
    if response.status_code == 200:
        with open(f"{person.lower()}_greeting.mp3", "wb") as f:
            f.write(response.content)
        print(f"✅ Generated for {person}")
    else:
        print(f"❌ Failed for {person}: {response.json()}")
```

### Custom Voice Settings

To customize voice settings (stability, similarity_boost), modify the `generate_speech_elevenlabs()` function in `main.py`:

```python
data = {
    "text": text,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.7,        # 0.0-1.0 (higher = more stable)
        "similarity_boost": 0.8  # 0.0-1.0 (higher = more similar)
    }
}
```

## Rate Limits

ElevenLabs free tier limits:
- **10,000 characters/month**
- **3 concurrent requests**

Paid tiers have higher limits. Check [elevenlabs.io/pricing](https://elevenlabs.io/pricing).
