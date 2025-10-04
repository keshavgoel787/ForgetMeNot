import google.generativeai as genai
import json

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_memory(transcript: str):
    """
    Uses Gemini to extract structured memory info.
    Returns a JSON dict with people, location, emotion, and summary.
    """
    prompt = f"""
    Analyze the following memory transcript and extract:
    - People mentioned
    - Location or setting
    - Main event or topic
    - Emotional tone (joyful, sad, nostalgic, confused, calm, anxious)
    - A short 1–2 sentence summary

    Return strictly as valid JSON with these keys:
    people, location, event, emotion, summary.

    Transcript:
    {transcript}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Try parsing JSON; fallback to raw text
    try:
        data = json.loads(response.text)
    except Exception:
        data = {"summary": response.text.strip()}

    return data
