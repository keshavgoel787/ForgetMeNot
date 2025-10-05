# Memory Context Analyzer

Automatically analyze images and videos in your memory folders using Google Gemini's vision and audio understanding capabilities.

## Features

- 🖼️ **Image Analysis**: Detailed descriptions of photos including people, activities, settings, and mood
- 🎥 **Video Analysis**: Comprehensive analysis including both visual content and audio (dialogue, sounds, atmosphere)
- 📝 **Automatic Context Generation**: Creates `filename_context` entries in `context.json` for each media file
- 🔄 **Batch Processing**: Processes all memory folders automatically

## Setup

### 1. Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a free API key
3. Copy the API key

### 2. Run Setup Script

```bash
cd processing_script
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment (`venv/`)
- Install all required dependencies
- Set up the project structure

### 3. Configure API Key

Edit the `.env` file and add your API key:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Run the Analyzer

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run the analyzer
python text_context_per_memory.py
```

## How It Works

The script will:

1. **Scan** all folders in `pre_processed/data/memories/`
2. **Analyze** each image and video file using Gemini's multimodal AI
3. **Generate** contextual descriptions for each file
4. **Update** `context.json` in each memory folder with:
   - `filename_context`: Detailed description of the media file

### Example Output

Your `context.json` will look like:

```json
{
  "memory_context": "day in college - A day of college life...",
  "gettingreadyforschool_context": "A student preparing for morning classes, organizing their backpack with books and materials in a dorm room setting.",
  "walkingwithfriendtolunch_context": "Two friends walking together across campus, engaged in animated conversation while heading to lunch on a sunny afternoon.",
  "saladfoodpic_context": "A healthy lunch featuring a fresh mixed green salad with colorful vegetables, presented on a cafeteria tray."
}
```

## Supported Formats

- **Images**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp`, `.gif`
- **Videos**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

## Video Analysis Capabilities

Gemini analyzes videos comprehensively:
- **Visual**: Activities, people, settings, objects
- **Audio**: Dialogue transcription, background sounds, music, tone
- **Context**: Overall story and emotional atmosphere

## Troubleshooting

**API Key Error**: Make sure your `.env` file has the correct API key

**Processing Failed**: Some large video files may take time to process. The script waits automatically.

**Rate Limits**: If you hit rate limits, the script will show errors. Wait a few minutes and try again.

## Dependencies

- `google-generativeai` - Gemini API client
- `python-dotenv` - Environment variable management
- `Pillow` - Image processing

## Notes

- First run may take time as videos are uploaded and processed
- The script preserves existing `memory_context` entries
- API usage is tracked by Google (free tier has limits)
