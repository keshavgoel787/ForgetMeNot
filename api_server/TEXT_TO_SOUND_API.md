# Text-to-Sound Effects & Music API

Generate high-quality sound effects and music from text descriptions using ElevenLabs' AI sound generation.

## Endpoint

```
POST /text-to-sound
```

## Description

Create custom sound effects, ambient audio, or music from simple text prompts. Perfect for:
- 🎮 Game sound effects
- 🎬 Video production
- 🎵 Music creation
- 🌧️ Ambient soundscapes
- 🔊 Audio for presentations

## Request

**Content-Type:** `application/json`

### Body Parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | - | Description of the sound/music to generate |
| `duration_seconds` | float | No | Auto | Length of audio (0.5-30 seconds) |
| `prompt_influence` | float | No | 0.3 | How closely to follow prompt (0-1) |

### Parameter Details

**`text`** - Text description of the sound/music:
- Be specific and descriptive
- Include genre, mood, instruments for music
- Include action and materials for sound effects
- Examples:
  - "Epic orchestral music with rising tension"
  - "Gentle rain falling on leaves"
  - "Glass shattering on concrete floor"
  - "Upbeat electronic dance music with heavy bass"

**`duration_seconds`** (optional):
- Range: 0.5 to 30 seconds
- If not specified, AI determines optimal duration
- Longer = more development of musical themes

**`prompt_influence`** (optional):
- Range: 0.0 to 1.0
- **Low (0-0.3):** More creative, varied interpretations
- **Medium (0.4-0.6):** Balanced creativity and accuracy
- **High (0.7-1.0):** Strict adherence to prompt

## Response

**Status:** `200 OK`

**Content-Type:** `audio/mpeg`

Returns an MP3 file ready to download or play.

## Usage Examples

### cURL

```bash
# Generate epic music
curl -X POST http://localhost:8000/text-to-sound \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Epic cinematic orchestral music with drums and strings",
    "duration_seconds": 15,
    "prompt_influence": 0.5
  }' \
  --output epic_music.mp3

# Generate sound effect (auto duration)
curl -X POST http://localhost:8000/text-to-sound \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Door creaking open slowly"
  }' \
  --output door_creak.mp3
```

### Python (requests)

```python
import requests

# Generate dramatic music
response = requests.post(
    'http://localhost:8000/text-to-sound',
    json={
        'text': 'Dramatic piano music with emotional melody',
        'duration_seconds': 20,
        'prompt_influence': 0.6
    }
)

if response.status_code == 200:
    with open('dramatic_piano.mp3', 'wb') as f:
        f.write(response.content)
    print('✅ Music saved: dramatic_piano.mp3')
else:
    print(f'❌ Error: {response.json()}')
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:8000/text-to-sound', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'Upbeat electronic dance music',
    duration_seconds: 10,
    prompt_influence: 0.4
  })
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'edm_track.mp3';
  a.click();
  console.log('✅ Music downloaded!');
})
.catch(error => console.error('❌ Error:', error));
```

### Python (Advanced - Multiple generations)

```python
import requests

# Generate a library of sound effects
sound_effects = [
    "Thunder rumbling in the distance",
    "Footsteps on gravel path",
    "Wind howling through trees",
    "Birds chirping in forest",
    "Water dripping in cave"
]

for idx, description in enumerate(sound_effects):
    response = requests.post(
        'http://localhost:8000/text-to-sound',
        json={
            'text': description,
            'duration_seconds': 5,
            'prompt_influence': 0.5
        }
    )
    
    if response.status_code == 200:
        filename = f"sfx_{idx+1:02d}_{description[:20].replace(' ', '_')}.mp3"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'✅ Generated: {filename}')
    else:
        print(f'❌ Failed: {description}')
```

## Prompt Examples

### 🎵 Music

**Classical:**
```json
{"text": "Peaceful piano composition with gentle melody"}
{"text": "Baroque string quartet with harpsichord"}
{"text": "Romantic violin solo with orchestra accompaniment"}
```

**Modern:**
```json
{"text": "Upbeat electronic dance music with heavy bass drops"}
{"text": "Lo-fi hip hop beats with vinyl crackle"}
{"text": "Ambient techno with atmospheric pads"}
```

**Cinematic:**
```json
{"text": "Epic orchestral trailer music with dramatic brass and percussion"}
{"text": "Dark suspenseful music with low strings and dissonant notes"}
{"text": "Heroic adventure theme with soaring melodies"}
```

### 🔊 Sound Effects

**Nature:**
```json
{"text": "Gentle rain falling on leaves with distant thunder"}
{"text": "Ocean waves crashing on rocky shore"}
{"text": "Wind rustling through autumn leaves"}
{"text": "Crackling campfire with popping embers"}
```

**Action:**
```json
{"text": "Glass shattering on concrete floor"}
{"text": "Car engine revving and screeching tires"}
{"text": "Sword clashing against metal shield"}
{"text": "Explosion with debris falling"}
```

**Ambience:**
```json
{"text": "Busy city street with cars and distant sirens"}
{"text": "Quiet library with occasional page turning"}
{"text": "Haunted house with creaking floorboards and whispers"}
{"text": "Spaceship bridge with electronic beeps and hums"}
```

**UI/Game:**
```json
{"text": "Button click sound, crisp and satisfying"}
{"text": "Level up fanfare with ascending notes"}
{"text": "Error notification sound, gentle alert"}
{"text": "Coin collection sound, bright and cheerful"}
```

## Error Responses

### Missing API Key

**Status:** `500 Internal Server Error`

```json
{
  "detail": "ELEVENLABS_API_KEY not configured"
}
```

### Invalid Duration

**Status:** `400 Bad Request`

```json
{
  "detail": "duration_seconds must be between 0.5 and 30 seconds"
}
```

### Invalid Prompt Influence

**Status:** `400 Bad Request`

```json
{
  "detail": "prompt_influence must be between 0 and 1"
}
```

### ElevenLabs API Error

**Status:** Varies (400-500)

```json
{
  "detail": "ElevenLabs API error: <error message>"
}
```

## Configuration

Add to your `.env` file:

```bash
ELEVENLABS_API_KEY=your_api_key_here
```

Get your API key:
1. Sign up at https://elevenlabs.io
2. Go to Settings → API Keys
3. Copy your key

## Performance & Limits

### Generation Time
- **Short sounds (<5s):** ~10-15 seconds
- **Medium sounds (5-15s):** ~20-30 seconds  
- **Long sounds (15-30s):** ~30-45 seconds

### Quality
- Output format: MP3 (44.1kHz, 192kbps)
- High-quality AI-generated audio
- Professional-grade results

### ElevenLabs Credits
Each sound generation consumes credits:
- **Short sound (<5s):** ~1-2 credits
- **Medium sound (5-15s):** ~3-5 credits
- **Long sound (15-30s):** ~6-10 credits

Check your usage at https://elevenlabs.io/account

## Best Practices

### ✅ DO:

**Be Descriptive:**
- ❌ "Music"
- ✅ "Upbeat electronic dance music with pulsing bass and energetic drums"

**Specify Mood/Genre:**
- ❌ "Sad sound"
- ✅ "Melancholic piano melody with minor chords and slow tempo"

**Include Details:**
- ❌ "Rain"
- ✅ "Heavy rain falling on metal roof with thunder in distance"

**Use Musical Terms:**
- ✅ "Staccato strings with legato cello"
- ✅ "Crescendo to forte with timpani rolls"

### ❌ DON'T:

- Use vague descriptions ("nice sound", "cool music")
- Request copyrighted music ("Play Bohemian Rhapsody")
- Expect instant results (AI generation takes time)
- Generate extremely long audio (max 30s per request)
- Use for real-time applications (latency ~10-45s)

## Tips for Better Results

### 🎵 For Music:

1. **Specify genre clearly:**
   - "Jazz piano trio with walking bass"
   - "Heavy metal guitar riff with double bass drums"

2. **Describe tempo:**
   - "Slow and melancholic"
   - "Fast-paced and energetic"
   - "Moderate tempo, steady rhythm"

3. **Name instruments:**
   - "Acoustic guitar, violin, and cello"
   - "Synthesizers and electronic drums"

4. **Set the mood:**
   - "Joyful and uplifting"
   - "Dark and mysterious"
   - "Calm and peaceful"

### 🔊 For Sound Effects:

1. **Include action + object:**
   - "Door slamming shut"
   - "Glass breaking"
   - "Footsteps running"

2. **Specify materials:**
   - "Wood creaking"
   - "Metal clanging"
   - "Fabric tearing"

3. **Add environment:**
   - "Echoing in large hall"
   - "Muffled through wall"
   - "Reverberating in canyon"

4. **Describe intensity:**
   - "Gentle tapping"
   - "Loud explosion"
   - "Subtle rustling"

## Use Cases

### 1. **Game Development**
```python
# Generate UI sounds
ui_sounds = {
    "button_click": "Sharp digital click sound",
    "menu_open": "Smooth whoosh transition",
    "error": "Soft warning beep",
    "success": "Cheerful ascending chime"
}

for name, description in ui_sounds.items():
    response = requests.post(
        'http://localhost:8000/text-to-sound',
        json={'text': description, 'duration_seconds': 1}
    )
    with open(f'{name}.mp3', 'wb') as f:
        f.write(response.content)
```

### 2. **Video Production**
```python
# Background music for different scenes
scenes = [
    ("intro", "Uplifting corporate music with piano and strings", 15),
    ("action", "Intense dramatic music with heavy percussion", 30),
    ("outro", "Calm reflective piano music fading out", 10)
]

for name, description, duration in scenes:
    response = requests.post(
        'http://localhost:8000/text-to-sound',
        json={
            'text': description,
            'duration_seconds': duration,
            'prompt_influence': 0.6
        }
    )
    with open(f'{name}_music.mp3', 'wb') as f:
        f.write(response.content)
```

### 3. **Podcast/Audio Production**
```python
# Transition sounds
transitions = [
    "Smooth fade transition with ambient pad",
    "Energetic stinger for segment change",
    "Subtle whoosh for topic shift"
]

for idx, description in enumerate(transitions):
    response = requests.post(
        'http://localhost:8000/text-to-sound',
        json={
            'text': description,
            'duration_seconds': 3,
            'prompt_influence': 0.4
        }
    )
    with open(f'transition_{idx+1}.mp3', 'wb') as f:
        f.write(response.content)
```

### 4. **App Notifications**
```python
# Custom notification sounds
notifications = {
    "message": "Gentle marimba notification tone",
    "alert": "Urgent but not alarming bell sound",
    "reminder": "Soft chime reminder",
    "achievement": "Triumphant fanfare with brass"
}

for name, description in notifications.items():
    response = requests.post(
        'http://localhost:8000/text-to-sound',
        json={
            'text': description,
            'duration_seconds': 2,
            'prompt_influence': 0.7
        }
    )
    with open(f'notif_{name}.mp3', 'wb') as f:
        f.write(response.content)
```

## Interactive Testing

Start the server and visit:
```
http://localhost:8000/docs
```

Find **`POST /text-to-sound`** and click **"Try it out"** to:
- Enter your text description
- Adjust duration and prompt influence
- Generate and download audio instantly
- Test different prompts interactively

## Troubleshooting

### "ELEVENLABS_API_KEY not configured"
**Problem:** API key missing or not loaded

**Solutions:**
- Add key to `.env` file
- Restart the server after adding
- Check for typos in variable name
- Ensure `.env` is in correct directory

### "Duration must be between 0.5 and 30 seconds"
**Problem:** Invalid duration parameter

**Solutions:**
- Use value between 0.5 and 30
- Or omit duration to let AI decide
- Split longer audio into multiple requests

### "Prompt influence must be between 0 and 1"
**Problem:** Invalid prompt_influence value

**Solutions:**
- Use value between 0.0 and 1.0
- Default is 0.3 (balanced)
- Adjust based on desired creativity

### Poor Quality Results
**Problem:** Generated audio doesn't match expectations

**Solutions:**
- Be more specific in description
- Try different prompt_influence values
- Include more musical/audio details
- Reference genres, instruments, moods
- Experiment with different phrasings

## Cost Estimation

**ElevenLabs Pricing (as of 2024):**
- Free tier: Limited credits/month
- Each sound: ~1-10 credits (based on duration)
- **Estimated free tier:** 10-50 sounds/month

For production:
- Creator plan: $22/month
- Pro plan: $99/month
- Check latest: https://elevenlabs.io/pricing

## Comparison with Text-to-Speech

| Feature | Text-to-Speech | Text-to-Sound |
|---------|----------------|---------------|
| **Input** | Text to speak | Sound description |
| **Output** | Human voice | Sound effects/music |
| **Use Case** | Narration, dialogue | Ambience, SFX, music |
| **Duration** | Any length | 0.5-30 seconds |
| **Voice** | Cloned voices | N/A |
| **Customization** | Voice selection | Prompt influence |

## Combining Endpoints

Create complete audio experiences by combining endpoints:

```python
import requests

# Step 1: Generate background music
music_response = requests.post(
    'http://localhost:8000/text-to-sound',
    json={
        'text': 'Calm ambient background music',
        'duration_seconds': 30
    }
)

# Step 2: Generate voiceover
voice_response = requests.post(
    'http://localhost:8000/text-to-speech',
    json={
        'text': 'Welcome to our application!',
        'name': 'Hannah'
    }
)

# Step 3: Generate notification sound
notif_response = requests.post(
    'http://localhost:8000/text-to-sound',
    json={
        'text': 'Success notification chime',
        'duration_seconds': 2
    }
)

# Save all files
with open('bg_music.mp3', 'wb') as f:
    f.write(music_response.content)
with open('voiceover.mp3', 'wb') as f:
    f.write(voice_response.content)
with open('notification.mp3', 'wb') as f:
    f.write(notif_response.content)

# Mix them together using audio editing tools
# (FFmpeg, Pydub, etc.)
```

## Support

- **ElevenLabs Docs:** https://elevenlabs.io/docs/capabilities/sound-effects
- **API Reference:** https://elevenlabs.io/docs/api-reference/text-to-sound-effects
- **Community:** https://discord.gg/elevenlabs

---

**Create any sound you can imagine! 🎵🔊** Just describe it in text and get professional-quality audio in seconds.
