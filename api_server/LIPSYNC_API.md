# Lip-Sync Video Generation API

Create realistic talking head videos from a still image and audio file using Gooey.AI's lip-sync technology.

## Endpoint

```
POST /lipsync
```

## Prerequisites

You need a **Gooey.AI API key**:

1. Sign up at https://gooey.ai
2. Go to Settings → API Keys
3. Copy your API key
4. Add to `.env` file:
   ```
   GOOEY_API_KEY=sk-your-key-here
   ```

## Request

**Content-Type:** `multipart/form-data`

### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | File | Yes | Still image or video (jpg, png, mp4, mov) |
| `audio` | File | Yes | Audio file (mp3, wav) |

### Requirements

**Image:**
- Formats: JPG, PNG, MP4, MOV
- Must contain a clear human face
- Face should have visible eyes, nose, and lips
- Non-human faces will not work

**Audio:**
- Formats: MP3, WAV
- Any length supported
- Audio will be matched to lip movements

## Response

**Status:** `200 OK`

```json
{
  "status": "success",
  "video_url": "https://storage.googleapis.com/.../lipsync_output.mp4",
  "gooey_url": "https://gooey.ai/Lipsync/?run_id=abc123",
  "run_id": "abc123",
  "message": "Lip-sync video generated successfully!"
}
```

### Response Fields

- **`video_url`** - Direct URL to download the generated MP4 video
- **`gooey_url`** - Link to view the result on Gooey.AI website
- **`run_id`** - Unique ID for this generation
- **`status`** - Always "success" if request succeeded
- **`message`** - Confirmation message

## Usage Examples

### cURL

```bash
curl -X POST http://localhost:8000/lipsync \
  -F "image=@photo.jpg" \
  -F "audio=@speech.mp3" \
  --output response.json

# Download the video
VIDEO_URL=$(cat response.json | jq -r '.video_url')
curl "$VIDEO_URL" --output talking_head.mp4
```

### Python (requests)

```python
import requests

# Upload files
files = {
    'image': open('photo.jpg', 'rb'),
    'audio': open('speech.mp3', 'rb')
}

response = requests.post(
    'http://localhost:8000/lipsync',
    files=files
)

if response.status_code == 200:
    result = response.json()
    video_url = result['video_url']
    
    # Download the video
    video_response = requests.get(video_url)
    with open('output.mp4', 'wb') as f:
        f.write(video_response.content)
    
    print(f"✅ Video saved: output.mp4")
    print(f"🌐 View online: {result['gooey_url']}")
else:
    print(f"❌ Error: {response.json()}")
```

### JavaScript (fetch)

```javascript
const formData = new FormData();
formData.append('image', imageFile);  // File from <input type="file">
formData.append('audio', audioFile);

fetch('http://localhost:8000/lipsync', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Video URL:', data.video_url);
  
  // Download the video
  const link = document.createElement('a');
  link.href = data.video_url;
  link.download = 'lipsync_video.mp4';
  link.click();
})
.catch(error => console.error('Error:', error));
```

### Combined with Text-to-Speech

Create a complete workflow: text → speech → lip-sync video!

```python
import requests

# Step 1: Generate speech from text
tts_response = requests.post(
    'http://localhost:8000/text-to-speech',
    json={
        'text': 'Hello! This is a test of the lip-sync feature.',
        'name': 'Hannah'
    }
)

# Save the generated audio
with open('generated_speech.mp3', 'wb') as f:
    f.write(tts_response.content)

# Step 2: Create lip-sync video
files = {
    'image': open('hannah_photo.jpg', 'rb'),
    'audio': open('generated_speech.mp3', 'rb')
}

lipsync_response = requests.post(
    'http://localhost:8000/lipsync',
    files=files
)

result = lipsync_response.json()
print(f"✅ Talking head video: {result['video_url']}")
```

## Error Responses

### Missing API Key

**Status:** `500 Internal Server Error`

```json
{
  "detail": "GOOEY_API_KEY not configured. Get your API key from https://gooey.ai"
}
```

### Invalid File Format

**Status:** `400 Bad Request`

```json
{
  "detail": "Invalid image format. Supported: .jpg, .jpeg, .png, .mp4, .mov"
}
```

### Gooey.AI API Error

**Status:** `4xx` or `500`

```json
{
  "detail": "Gooey.AI API error: <error message>"
}
```

### Timeout

**Status:** `504 Gateway Timeout`

```json
{
  "detail": "Video generation timed out. Try with shorter audio or smaller image."
}
```

## Configuration

Add to your `.env` file:

```bash
GOOEY_API_KEY=sk-your-actual-key-here
```

Get your API key from:
1. https://gooey.ai
2. Sign in / Sign up
3. Settings → API Keys
4. Copy the key

## Performance & Limits

### Processing Time
- **Small images + short audio (<10s):** ~30-60 seconds
- **Large images + long audio (>30s):** ~2-3 minutes
- **Maximum timeout:** 2 minutes (configurable)

### File Size Recommendations
- **Image:** < 5MB for faster processing
- **Audio:** < 10MB, < 2 minutes duration
- **Output video:** Similar length to input audio

### Gooey.AI Credits
Each lip-sync generation consumes Gooey.AI credits. Check your plan at https://gooey.ai/account

**Free tier:** Limited credits per month
**Paid plans:** More credits + faster processing

## Best Practices

### ✅ DO:
- Use high-quality, well-lit images
- Ensure face is clearly visible and front-facing
- Use clear audio with minimal background noise
- Keep videos under 2 minutes for faster processing
- Test with small files first

### ❌ DON'T:
- Use images without clear human faces
- Use heavily compressed or blurry images
- Upload extremely long audio files (>5 min)
- Expect instant results (processing takes time)
- Use for deepfakes or misleading content

## Interactive Testing

Start the server and visit:
```
http://localhost:8000/docs
```

Find the **`POST /lipsync`** endpoint and click **"Try it out"** to:
- Upload files directly in the browser
- See the API response in real-time
- Download the generated video

## Troubleshooting

### "No face detected"
**Problem:** Image doesn't contain a recognizable human face

**Solutions:**
- Use a photo with a clear, front-facing human face
- Ensure eyes, nose, and lips are visible
- Avoid heavily shadowed or obscured faces
- Try a different photo

### "Video generation timed out"
**Problem:** Processing took longer than 2 minutes

**Solutions:**
- Use a shorter audio file
- Reduce image resolution
- Try again (sometimes server load varies)
- Increase timeout in code if self-hosting

### "Invalid API key"
**Problem:** GOOEY_API_KEY is wrong or expired

**Solutions:**
- Check the API key in your `.env` file
- Regenerate key from https://gooey.ai/settings
- Ensure no extra spaces in the key
- Restart the server after updating .env

### "Credits exhausted"
**Problem:** You've used all your Gooey.AI credits

**Solutions:**
- Upgrade your Gooey.AI plan
- Wait for monthly credit reset
- Check usage at https://gooey.ai/account

## Use Cases

### 1. **Personalized Video Messages**
```python
# Create a birthday message from a photo
files = {
    'image': open('friend_photo.jpg', 'rb'),
    'audio': open('birthday_message.mp3', 'rb')
}
```

### 2. **Educational Content**
```python
# Make historical figures "speak"
files = {
    'image': open('einstein.jpg', 'rb'),
    'audio': open('physics_explanation.mp3', 'rb')
}
```

### 3. **Product Demos**
```python
# Create spokesperson videos
files = {
    'image': open('spokesperson.jpg', 'rb'),
    'audio': open('product_pitch.mp3', 'rb')
}
```

### 4. **Social Media Content**
```python
# Automated content generation
for audio_file in audio_files:
    files = {
        'image': open('profile_pic.jpg', 'rb'),
        'audio': open(audio_file, 'rb')
    }
    # Generate video...
```

## Advanced Options

The current implementation uses Gooey.AI's default settings. For more control, you can modify the `payload` in the code:

```python
# In main.py, modify the data dict:
data = {
    'json': json.dumps({
        'lipsync_model': 'Wav2Lip',  # or 'SadTalker'
        'face_padding_top': 0,
        'face_padding_bottom': 10,
        'face_padding_left': 0,
        'face_padding_right': 0,
    })
}
```

See Gooey.AI docs for all available options: https://docs.gooey.ai

## Cost Estimation

**Gooey.AI Pricing (as of 2024):**
- Free tier: ~100 credits/month
- Each lip-sync: ~10-20 credits
- **Estimated free tier:** 5-10 videos/month

For production use, consider:
- Gooey.AI Pro plan: $30/month
- Pay-as-you-go: $0.10-0.50 per video
- Check latest pricing: https://gooey.ai/pricing

## Security & Privacy

### Data Handling
- Files are sent to Gooey.AI for processing
- Generated videos are stored on Gooey.AI's servers
- URLs are publicly accessible (no authentication)
- Consider privacy implications for sensitive content

### Recommendations
- Don't use for confidential/private faces
- Read Gooey.AI privacy policy: https://gooey.ai/privacy
- For sensitive use cases, consider self-hosted solutions
- Delete generated videos from Gooey.AI after download

## Support

- **Gooey.AI Docs:** https://docs.gooey.ai
- **Gooey.AI Community:** https://discord.gg/gooeyai
- **API Status:** https://status.gooey.ai

## Example Response

Complete example of a successful response:

```json
{
  "status": "success",
  "video_url": "https://storage.googleapis.com/dara-c1b52.appspot.com/daras_ai/media/5abbbb76-eb36-11ee-8c54-02420a00014c/gooey.ai%20lipsync.mp4",
  "gooey_url": "https://gooey.ai/Lipsync/?run_id=m0rghxk55xfx&uid=fm165fOmucZlpa5YHupPBdcvDR02",
  "run_id": "m0rghxk55xfx",
  "message": "Lip-sync video generated successfully!"
}
```

The `video_url` is a direct download link that expires after some time. Download and save the video if you need permanent access.

---

**Ready to create talking head videos! 🎬** Just upload an image and audio file to get a professional lip-synced video in seconds.
