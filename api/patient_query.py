"""
Patient Query API - 6-Mode Classification and Response System

Handles patient requests by:
1. Transcribing audio
2. Classifying intent → display mode
3. Retrieving memories from Snowflake
4. Selecting appropriate media
5. Generating narration (if needed)
6. Returning formatted response
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List, Dict
import tempfile
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from scripts.lib.snowflake_client import SnowflakeClient
from scripts.retrieval_cycle import search_memories_by_query, format_memories_for_gemini
from scripts.lib.gemini_client import generate_text
from api.schemas import PatientQueryResponse
from api.intent_classifier import classify_intent_and_media
import google.generativeai as genai

router = APIRouter(prefix="/patient", tags=["Patient"])

# Import experiences storage from therapist module
from api.experiences import experiences

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def transcribe_audio_file(audio_path: str) -> str:
    """Transcribe audio file using Gemini"""
    try:
        audio_file = genai.upload_file(path=audio_path)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """Transcribe this audio recording. This is from an Alzheimer's patient.

Instructions:
- Transcribe exactly what is said
- Preserve the patient's words and intent
- If unclear, indicate with [unclear]

Provide only the transcription:"""

        response = model.generate_content([audio_file, prompt])
        genai.delete_file(audio_file.name)

        return response.text.strip()
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")


def select_media_for_mode(display_mode: str, memories: List[tuple]) -> List[str]:
    """Select appropriate media URLs based on display mode"""
    images = []
    horizontal_videos = []
    vertical_videos = []

    for memory in memories:
        event_name, file_name, file_type, description, people, event_summary, file_url, similarity = memory

        if file_type.lower() == "image":
            images.append(file_url)
        elif file_type.lower() == "video":
            if "vertical" in description.lower() or "portrait" in description.lower():
                vertical_videos.append(file_url)
            else:
                horizontal_videos.append(file_url)

    # Select based on mode
    if display_mode == "4-pic":
        return images[:4]
    elif display_mode == "3-pic":
        return images[:3]
    elif display_mode == "5-pic":
        return images[:5]
    elif display_mode == "video":
        return horizontal_videos[:1] if horizontal_videos else (images[:1] if images else [])
    elif display_mode == "vertical-video":
        return vertical_videos[:1] if vertical_videos else (horizontal_videos[:1] if horizontal_videos else [])
    elif display_mode == "agent":
        # Agent mode will generate lip-sync video - placeholder for now
        return ["https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"]

    return []


def generate_narration(topic: str, memories_context: str, transcription: str) -> str:
    """Generate warm narration text using Gemini"""

    prompt = f"""You are creating a gentle, warm narration for an Alzheimer's patient about their memories.

**Context:**
Patient asked: "{transcription}"
Topic: "{topic}"

**Retrieved Memories:**
{memories_context}

**Your Task:**
Create a 2-3 sentence narration that:
1. Addresses what the patient asked about
2. Highlights specific details from the memories (people, places, activities)
3. Uses warm, emotionally supportive language
4. Speaks in second person ("you were...", "you enjoyed...")
5. Sounds like a caring family member reminiscing with them

**Narration Style Examples:**
- "Remember these special moments with Avery at the beach? The sun was shining, and she was so excited to play in the sand."
- "College days were full of excitement and new adventures. From late night study sessions to celebrating with friends, these photos capture your energy and enthusiasm."

**Generate narration now (2-3 sentences only):**"""

    try:
        narration = generate_text(
            prompt,
            model_name="gemini-2.5-flash",
            temperature=0.8,
            max_tokens=200
        )
        return narration
    except Exception as e:
        # Fallback narration
        return f"Here are beautiful memories about {topic}. These moments capture special times that are worth treasuring forever."


@router.post("/query", response_model=PatientQueryResponse)
async def patient_query(
    audio_file: UploadFile = File(..., description="MP3 audio file from patient"),
    topic: str = Form(..., description="Topic/person/event (e.g., 'Avery', 'College')")
):
    """
    **Patient Query Endpoint** - 6-Mode Classification System

    Takes patient audio + topic and returns appropriate response:
    - 4-pic: 4 images + narration
    - 3-pic: 3 images + narration
    - 5-pic: 5 images + narration
    - video: Horizontal video + narration
    - vertical-video: Vertical video + narration
    - agent: Conversational lip-sync video (no text)

    **Example Request:**
    ```
    POST /patient/query
    Form Data:
    - audio_file: <patient_audio.mp3>
    - topic: "Avery"
    ```

    **Example Responses:**

    Memory Replay (4-pic):
    ```json
    {
      "topic": "Avery",
      "text": "Remember these special moments with Avery at the beach?...",
      "displayMode": "4-pic",
      "media": ["url1.jpg", "url2.jpg", "url3.jpg", "url4.jpg"]
    }
    ```

    Agent Conversation:
    ```json
    {
      "topic": "Avery",
      "text": null,
      "displayMode": "agent",
      "media": ["lip_sync_video.mp4"]
    }
    ```
    """

    temp_path = None
    try:
        # Step 1: Save uploaded audio
        temp_path = f"/tmp/{audio_file.filename}"
        with open(temp_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)

        # Step 2: Transcribe audio
        transcription = transcribe_audio_file(temp_path)
        print(f"📝 Transcription: {transcription}")

        # Step 3: Classify intent and get display mode
        with SnowflakeClient() as client:
            display_mode, media_info = classify_intent_and_media(
                transcription, topic, client
            )
            print(f"🎯 Display Mode: {display_mode}")

            # Step 4: Retrieve memories
            memories = search_memories_by_query(topic, client, top_k=15)

            if not memories:
                raise HTTPException(
                    status_code=404,
                    detail=f"No memories found for topic: {topic}"
                )

            # Step 5: Select media based on display mode
            media_urls = select_media_for_mode(display_mode, memories)

            # Step 6: Generate narration (if not agent mode)
            narration_text = None
            if display_mode != "agent":
                memories_context = format_memories_for_gemini(memories[:5])
                narration_text = generate_narration(topic, memories_context, transcription)
                print(f"💬 Narration: {narration_text}")

            # Step 7: Return response
            return PatientQueryResponse(
                topic=topic,
                text=narration_text,
                displayMode=display_mode,
                media=media_urls
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/query-test", response_model=PatientQueryResponse)
async def patient_query_test(
    transcription: str = Form(..., description="Test transcription (skip audio upload)"),
    topic: str = Form(..., description="Topic/person/event")
):
    """
    **Test endpoint** - Bypass audio upload, provide transcription directly

    Useful for testing the classification and response system without audio files.

    **Example:**
    ```
    POST /patient/query-test
    Form Data:
    - transcription: "I want to learn more about the beach day and when we got ice cream"
    - topic: "Avery"
    ```
    """

    try:
        # Skip transcription, use provided text
        print(f"📝 Test Transcription: {transcription}")

        # Classify intent and get display mode
        with SnowflakeClient() as client:
            display_mode, media_info = classify_intent_and_media(
                transcription, topic, client
            )
            print(f"🎯 Display Mode: {display_mode}")

            # Retrieve memories
            memories = search_memories_by_query(topic, client, top_k=15)

            if not memories:
                raise HTTPException(
                    status_code=404,
                    detail=f"No memories found for topic: {topic}"
                )

            # Select media
            media_urls = select_media_for_mode(display_mode, memories)

            # Generate narration (if not agent mode)
            narration_text = None
            if display_mode != "agent":
                memories_context = format_memories_for_gemini(memories[:5])
                narration_text = generate_narration(topic, memories_context, transcription)
                print(f"💬 Narration: {narration_text}")

            return PatientQueryResponse(
                topic=topic,
                text=narration_text,
                displayMode=display_mode,
                media=media_urls
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/experience/{experience_id}")
async def view_experience(experience_id: str):
    """
    **Patient Endpoint**: View an experience created by therapist.

    The patient accesses this URL to see their assigned memory experience.
    """

    if experience_id not in experiences:
        raise HTTPException(
            status_code=404,
            detail=f"Experience {experience_id} not found"
        )

    return {
        "status": "success",
        "experience": experiences[experience_id]
    }


@router.get("/experiences")
async def list_patient_experiences(limit: int = 10):
    """
    **Patient Endpoint**: List all available experiences.

    Returns all experiences auto-assigned to the patient (all created by therapist).
    """

    recent = list(experiences.values())[-limit:]

    return {
        "status": "success",
        "total": len(experiences),
        "experiences": [
            {
                "experience_id": exp["experience_id"],
                "title": exp["title"],
                "created_at": exp["created_at"],
                "total_memories": exp["total_memories"]
            }
            for exp in reversed(recent)
        ]
    }
