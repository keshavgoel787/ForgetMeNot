# ElevenLabs Voice Clone Upload

This script uploads voice samples to ElevenLabs to create AI voice clones.

## Prerequisites

1. **ElevenLabs Account**
   - Sign up at [elevenlabs.io](https://elevenlabs.io)
   - Get your API key from Settings → Profile

2. **Voice Files**
   - Run `extract_person_audio.py` first to create voice files
   - Each person should have a `{name}_voice.mp3` file

3. **Dependencies**
   ```bash
   pip install requests
   ```

## Setup

Set your ElevenLabs API key as an environment variable:

```bash
export ELEVENLABS_API_KEY='your_api_key_here'
```

Or add it to your `.env` file:
```
ELEVENLABS_API_KEY=your_api_key_here
```

## Usage

```bash
python upload_voices_to_elevenlabs.py
```

## What It Does

1. **Finds voice files** - Scans `pre_processed/data/people/` for all `*_voice.mp3` files
2. **Checks existing voices** - Lists voices already in your ElevenLabs account
3. **Uploads new voices** - Creates voice clones for anyone who doesn't already exist
4. **Names them** - Uses format `{name}_voice_forgetmenot` (e.g., `Tyler_voice_forgetmenot`)

## Output

Each successfully uploaded voice will have:
- **Name**: `{person_name}_voice_forgetmenot`
- **Voice ID**: Unique identifier for API calls
- **Description**: "Voice clone of {name} from ForgetMeNot project"

## Example

If you have these voice files:
```
people/
├── Tyler/Tyler_voice.mp3
├── Hannah/Hannah_voice.mp3
├── Steve/Steve_voice.mp3
```

The script will create in ElevenLabs:
- `Tyler_voice_forgetmenot`
- `Hannah_voice_forgetmenot`
- `Steve_voice_forgetmenot`

## Voice Clone Quality

For best results, voice samples should:
- ✅ Be at least 30 seconds long
- ✅ Have clear, consistent audio quality
- ✅ Contain only one speaker
- ✅ Have minimal background noise

The `extract_person_audio.py` script automatically creates these from solo videos.

## API Limits

**Free tier:**
- 10 custom voices max
- 10,000 characters/month

**Paid plans:**
- More custom voices
- Higher character limits
- Better voice quality

Check [elevenlabs.io/pricing](https://elevenlabs.io/pricing) for details.

## Troubleshooting

### "ELEVENLABS_API_KEY not found"
Set the environment variable or add to `.env` file.

### "Voice already exists"
The script automatically skips voices that are already uploaded.

### "Failed to create voice"
Check:
- API key is valid
- You haven't exceeded voice limit
- Audio file is valid MP3
- Audio is at least a few seconds long

## Next Steps

After uploading, you can use these voices with the ElevenLabs API:

```python
import requests

voice_id = "your_voice_id_here"
api_key = "your_api_key"

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {"xi-api-key": api_key}
data = {"text": "Hello! This is my cloned voice."}

response = requests.post(url, headers=headers, json=data)
with open("output.mp3", "wb") as f:
    f.write(response.content)
```
