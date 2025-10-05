# Complete Pipeline - One Command Does It All

## 🚀 Quick Start

```bash
python RUN_ALL_PIPELINE.py
```

This runs **Steps 2, 3, 4, 5** automatically:
- ✅ **Step 2**: Convert person folders to actual names
- ✅ **Step 3**: Generate AI context with people identification
- ✅ **Step 4**: Extract audio from solo videos
- ✅ **Step 5**: Upload voice clones to ElevenLabs

**One command, complete automation!**

---

## 📋 Prerequisites

### **Step 1 must be completed first:**
```bash
python 1_extract_faces.py
```
This creates the `person_1/`, `person_2/`, etc. folders.

### **Required files:**
- `names.json` in `pre_processed/data/people/`
- `.env` file with API keys:
  ```
  GEMINI_API_KEY=your_gemini_key
  ELEVENLABS_API_KEY=your_elevenlabs_key
  ```

### **System dependencies:**
```bash
sudo dnf install ffmpeg
```

### **Python dependencies:**
Already installed if you ran Step 1.

---

## 🎯 What Each Step Does

### **Step 2: Name Conversion**
Converts `person_X/` folders to actual names:
```
person_1/ → Tyler/
person_2/ → Hannah/
person_3/ → Steve/
```

Supports:
- **Merging duplicates**: `"Tyler": "person_1,person_22,person_33"`
- **Deleting unwanted**: `"delete": "person_100,person_101"`

### **Step 3: Context Generation**
Uses Gemini AI to analyze videos/images:
- Identifies who appears in each video
- Generates descriptive context
- Saves to `context.json` in each memory folder

Example output:
```json
{
  "video1_context": "Tyler at a football game cheering for his team...",
  "video1_people": "Tyler"
}
```

### **Step 4: Audio Extraction**
Extracts audio from videos where only one person appears:
- Finds solo videos from context.json
- Extracts audio with ffmpeg
- Merges all clips per person
- Saves as `{name}_voice.mp3`

### **Step 5: ElevenLabs Upload**
Uploads voice samples to create AI voice clones:
- Uploads `{name}_voice.mp3` files
- Creates voice clones in ElevenLabs
- Names them `{name}_voice_forgetmenot`
- Returns Voice IDs for API use

---

## 📊 Expected Timeline

**Assuming 4 memories with ~10 videos each:**

| Step | Duration | Why |
|------|----------|-----|
| Step 2 | ~30 seconds | File operations |
| Step 3 | ~10-15 minutes | API calls (50 videos × ~15 sec) |
| Step 4 | ~2-3 minutes | Audio extraction |
| Step 5 | ~30 seconds | Voice uploads |

**Total:** ~15-20 minutes

---

## 🔧 Configuration

### **names.json Format:**

**Option 1: Name → Person(s)**
```json
{
  "Tyler": "person_1,person_22,person_33",
  "Hannah": "person_2",
  "Steve": "person_3",
  "delete": "person_100,person_200"
}
```

**Option 2: Person → Name**
```json
{
  "person_1": "Tyler",
  "person_2": "Hannah",
  "person_3": "Steve",
  "person_100": null
}
```

### **.env File:**
```bash
# Required for Step 3
GEMINI_API_KEY=your_gemini_api_key_here

# Required for Step 5 (optional, can skip)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

---

## 🎬 Example Run

```bash
$ python RUN_ALL_PIPELINE.py

======================================================================
🚀 COMPLETE PIPELINE: NAMES → CONTEXT → AUDIO → VOICES 🚀
======================================================================

This will run all steps:
  Step 2: Convert person_X folders to actual names
  Step 3: Generate AI context with people identification
  Step 4: Extract audio from solo videos
  Step 5: Upload to ElevenLabs for voice cloning

Continue with full pipeline? (y/n): y

======================================================================
STEP 2: NAME CONVERSION
======================================================================

📋 Current names.json:
{
  "Tyler": "person_1,person_22",
  "Hannah": "person_2",
  "Steve": "person_3"
}

Continue with this mapping? (y/n): y

🚀 Starting name conversion...
✅ STEP 2 COMPLETE!

⏭️ ⏭️ ⏭️ ... Moving to Step 3...

======================================================================
STEP 3: CONTEXT GENERATION
======================================================================

⚠️  WARNING: This will use Gemini API and may take a while!

Continue with context generation? (y/n): y

Loading people references...
  👤 Loaded 3 reference images for Tyler
  👤 Loaded 3 reference images for Hannah
  👤 Loaded 3 reference images for Steve

Processing folder 1/4: football trip
  🎥 Analyzing video: Football_trip_2.mp4
  ...

✅ STEP 3 COMPLETE!

⏭️ ⏭️ ⏭️ ... Moving to Step 4...

======================================================================
STEP 4: AUDIO EXTRACTION
======================================================================

📂 Processing: Tyler
  📹 Found 6 solo video(s)
  🎵 Extracting audio 1/6: Football_trip_2
  ...
  ✅ Saved: Tyler_voice.mp3

✅ Step 4 Complete: Extracted audio for 3 people

⏭️ ⏭️ ⏭️ ... Moving to Step 5...

======================================================================
STEP 5: ELEVENLABS UPLOAD
======================================================================

📁 Found 3 voice file(s)

[1/3] Tyler
  📤 Uploading...
  ✅ Created: Tyler_voice_forgetmenot
  Voice ID: abc123...

✅ Step 5 Complete: Uploaded 3, Skipped 0

🎉🎉🎉 ... 

======================================================================
✅ COMPLETE PIPELINE FINISHED!
======================================================================

✅ Names converted (Tyler/, Hannah/, Steve/)
✅ Context generated (context.json in each memory)
✅ Audio extracted (Tyler_voice.mp3, etc.)
✅ Voices uploaded to ElevenLabs

🎤 Your AI voice clones are ready to use!
```

---

## 🛠️ Troubleshooting

### **"names.json not found"**
Create it in `pre_processed/data/people/names.json`

### **"GEMINI_API_KEY not found"**
Add to `.env` file in processing_script/

### **"ffmpeg not found"**
Install: `sudo dnf install ffmpeg`

### **"ELEVENLABS_API_KEY not found"**
Step 5 will be skipped (optional). Add to `.env` if you want voice clones.

### **"API rate limit exceeded"**
Step 3 has 4-second delays between API calls. If you still hit limits:
- Wait 24 hours for quota reset
- Upgrade to paid Gemini API tier

### **"No solo videos found"**
Some people may not appear alone in any videos. They won't get voice files.

---

## 📁 Output Structure

```
pre_processed/data/
├── people/
│   ├── Tyler/
│   │   ├── Tyler_voice.mp3         ← Merged voice
│   │   ├── audio_clips/            ← Individual clips
│   │   └── face_*.jpg              ← Face images
│   ├── Hannah/
│   └── Steve/
│
└── memories/
    ├── football trip/
    │   ├── context.json            ← AI-generated context
    │   ├── Football_trip_2.mp4
    │   └── ...
    └── ...
```

---

## 🔄 Re-running

Safe to re-run! The pipeline automatically skips:
- ✅ Already renamed folders
- ✅ Already generated context
- ✅ Already extracted audio
- ✅ Already uploaded voices

Only processes what's missing.

---

## 🚀 Alternative: Run Steps Individually

If you prefer to run steps one at a time:

```bash
# Steps 2 & 3 together
python 2_3_name_and_context.py

# Steps 4 & 5 together
python 4_extract_and_upload_voices.py

# Or individually
python 2_convert_names.py
python 3_generate_context.py
python extract_person_audio.py
python upload_voices_to_elevenlabs.py
```

---

## 🎤 Using Your Voice Clones

After the pipeline completes, go to [elevenlabs.io](https://elevenlabs.io) to:
- Test your voice clones
- Generate speech in their voices
- Use the Voice IDs in your apps

Example API usage:
```python
import requests

voice_id = "your_tyler_voice_id"
api_key = "your_elevenlabs_key"

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {"xi-api-key": api_key}
data = {"text": "Hey! This is my cloned voice."}

response = requests.post(url, headers=headers, json=data)
with open("output.mp3", "wb") as f:
    f.write(response.content)
```

---

## 💡 Pro Tips

1. **Review names.json carefully** before running - name mapping affects all subsequent steps
2. **Check context.json after Step 3** - Verify people are correctly identified
3. **Keep voice samples** in audio_clips/ - Useful for debugging
4. **Save Voice IDs** from Step 5 - You'll need them for API calls
5. **Run during off-hours** - Step 3 takes 15+ minutes

---

**Questions?** Check the individual README files:
- `PEOPLE_EXTRACTION_README.md` - Step 1
- `FOLDER_EDITOR_README.md` - Step 2
- `ELEVENLABS_UPLOAD_README.md` - Step 5
