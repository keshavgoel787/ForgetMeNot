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
import random
import json

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from scripts.lib.snowflake_client import SnowflakeClient
from scripts.retrieval_cycle import search_memories_by_query, format_memories_for_gemini
from scripts.lib.gemini_client import generate_text
from api.schemas import PatientQueryResponse
from api.intent_classifier import classify_intent_and_media
from api.session_manager import session_manager
from api.conversation_history import conversation_history
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

        # Extract text from response
        transcription = response.candidates[0].content.parts[0].text

        genai.delete_file(audio_file.name)

        return transcription.strip()
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")


def filter_unseen_memories(memories: List[tuple], patient_id: str, topic: str) -> List[tuple]:
    """
    Filter out memories that have already been shown in this session
    """
    shown_ids = session_manager.get_shown_memories(patient_id, topic)

    # Filter out shown memories
    unseen = []
    for memory in memories:
        event_name, file_name, file_type, description, people, event_summary, file_url, similarity = memory

        # Use file_url as unique ID
        if file_url not in shown_ids:
            unseen.append(memory)

    print(f"🔍 Filtered: {len(memories)} total → {len(unseen)} unseen (skipped {len(shown_ids)} shown)")

    return unseen


def select_media_for_mode(display_mode: str, memories: List[tuple]) -> tuple[str, List[str]]:
    """
    Select appropriate media URLs based on display mode and available images.
    Adjusts display mode if not enough images are available.

    Returns: (adjusted_display_mode, media_urls)
    """
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

    # Handle photo modes - adjust based on available images
    if display_mode in ["4-pic", "3-pic", "5-pic"]:
        available_count = len(images)

        # Adjust display mode based on what's actually available
        if available_count >= 5:
            adjusted_mode = "5-pic" if display_mode == "5-pic" else display_mode
            return (adjusted_mode, images[:5] if adjusted_mode == "5-pic" else images[:int(display_mode[0])])
        elif available_count == 4:
            return ("4-pic", images[:4])
        elif available_count == 3:
            return ("3-pic", images[:3])
        else:
            # Less than 3 images, fallback to video
            if horizontal_videos:
                return ("video", horizontal_videos[:1])
            elif vertical_videos:
                return ("vertical-video", vertical_videos[:1])
            return (display_mode, [])

    # Video modes
    elif display_mode == "video":
        return (display_mode, horizontal_videos[:1] if horizontal_videos else (images[:1] if images else []))
    elif display_mode == "vertical-video":
        return (display_mode, vertical_videos[:1] if vertical_videos else (horizontal_videos[:1] if horizontal_videos else []))
    elif display_mode == "agent":
        # Agent mode will generate lip-sync video - placeholder for now
        return (display_mode, ["https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"])

    return (display_mode, [])


def generate_narration(
    topic: str,
    memories_context: str,
    transcription: str,
    patient_id: str
) -> str:
    """Generate warm narration text using Gemini with conversation history"""

    # Get conversation history
    conversation_context = conversation_history.get_formatted_history(patient_id, topic, max_turns=6)
    previous_responses = conversation_history.get_agent_previous_responses(patient_id, topic, max_turns=3)

    # Build context about what's been said before
    previous_context = ""
    if previous_responses:
        previous_context = f"""
**Previous responses you've given (DO NOT REPEAT THESE):**
{chr(10).join(f'- "{response}"' for response in previous_responses)}

IMPORTANT: Do not repeat the same phrases or information. Build on the conversation naturally.
"""

    prompt = f"""You are speaking to someone with Alzheimer's about their cherished memories. Talk to them like a close friend or family member who was there with them - warm, personal, and full of emotion.

They just said: "{transcription}"
You're talking about: {topic}

Here are the memories you're looking at together:
{memories_context}

{previous_context}

{conversation_context}

HOW TO SPEAK:
- Talk like you're sitting next to them, reminiscing together
- Use natural, conversational language - contractions, pauses, emotion
- Show genuine warmth and joy when describing happy moments
- Notice the little details that make memories special (a smile, laughter, the weather)
- Speak in second person as if YOU were there too: "Look at this - you were laughing so hard!", "I love seeing how happy you look here"
- Let your emotion show through your words - excitement, tenderness, nostalgia
- Vary your responses - don't always start the same way
- Keep it to 2-3 natural sentences, like you're actually talking

GOOD EXAMPLES (conversational, emotional, human):
- "Oh wow, look at you two at the beach! Avery was so little here - and you can just see how much fun she's having building that sandcastle with you."
- "Man, these college photos really take me back. You were always surrounded by friends, weren't you? This one from graduation day - you look so proud, and you should be!"
- "Here's another beautiful moment from Disney! See how the sun's hitting the castle just perfectly? You and the kids look absolutely magical standing there."
- "I remember this trip! The mountains were gorgeous that day. You've got that huge smile on your face - you always loved hiking, didn't you?"

Now respond naturally to what they said (2-3 sentences):"""

    try:
        narration = generate_text(
            prompt,
            model_name="gemini-2.5-flash",
            temperature=0.9,  # Higher temperature for more variety
            max_tokens=200
        )
        return narration
    except Exception as e:
        # Fallback narration
        return f"Here are beautiful memories about {topic}. These moments capture special times that are worth treasuring forever."


@router.post("/query", response_model=PatientQueryResponse)
async def patient_query(
    audio_file: UploadFile = File(..., description="MP3 audio file from patient"),
    topic: str = Form(..., description="Topic/person/event (e.g., 'Avery', 'College')"),
    patient_id: str = Form(default="default_patient", description="Patient ID for session tracking")
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

        # Step 3: Retrieve memories first
        with SnowflakeClient() as client:
            all_memories = search_memories_by_query(topic, client, top_k=50)

            if not all_memories:
                raise HTTPException(
                    status_code=404,
                    detail=f"No memories found for topic: {topic}"
                )

        # Step 4: Filter out already-shown memories
        unseen_memories = filter_unseen_memories(all_memories, patient_id, topic)

        # If all memories have been shown, reset and use all
        if not unseen_memories:
            print("♻️  All memories shown - resetting session")
            session_manager.reset_session(patient_id, topic)
            unseen_memories = all_memories

        # OPTIMIZATION: Run classification and narration in parallel
        import asyncio

        async def classify_task():
            with SnowflakeClient() as client:
                return classify_intent_and_media(transcription, topic, client)

        async def narration_task():
            memories_context = format_memories_for_gemini(unseen_memories[:5])
            return await asyncio.to_thread(
                generate_narration,
                topic,
                memories_context,
                transcription,
                patient_id
            )

        # Execute in parallel
        (display_mode, media_info), narration_text = await asyncio.gather(
            asyncio.to_thread(classify_task),
            narration_task()
        )

        print(f"🎯 Display Mode: {display_mode}")
        print(f"💬 Narration: {narration_text}")

        # Step 5: Select media based on display mode (adjusts mode if needed)
        adjusted_mode, media_urls = select_media_for_mode(display_mode, unseen_memories)
        print(f"📸 Adjusted Mode: {adjusted_mode} (from {display_mode}) - {len(media_urls)} media")

        # Step 5.5: Mark selected media as shown
        session_manager.mark_as_shown(patient_id, topic, media_urls)

        # Step 6: Save conversation history
        conversation_history.add_turn(patient_id, topic, "patient", transcription)

        if adjusted_mode != "agent":
            conversation_history.add_turn(patient_id, topic, "agent", narration_text)

        # Step 7: Return response
        return PatientQueryResponse(
            topic=topic,
            text=narration_text if adjusted_mode != "agent" else None,
            displayMode=adjusted_mode,
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
    topic: str = Form(..., description="Topic/person/event"),
    patient_id: str = Form(default="default_patient", description="Patient ID for session tracking")
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
            all_memories = search_memories_by_query(topic, client, top_k=50)

            if not all_memories:
                raise HTTPException(
                    status_code=404,
                    detail=f"No memories found for topic: {topic}"
                )

            # Filter out already-shown memories
            unseen_memories = filter_unseen_memories(all_memories, patient_id, topic)

            # If all memories have been shown, reset and use all
            if not unseen_memories:
                print("♻️  All memories shown - resetting session")
                session_manager.reset_session(patient_id, topic)
                unseen_memories = all_memories

            # Select media (adjusts mode if needed)
            adjusted_mode, media_urls = select_media_for_mode(display_mode, unseen_memories)
            print(f"📸 Adjusted Mode: {adjusted_mode} (from {display_mode}) - {len(media_urls)} media")

            # Mark selected media as shown
            session_manager.mark_as_shown(patient_id, topic, media_urls)

            # Save patient's question to conversation history
            conversation_history.add_turn(patient_id, topic, "patient", transcription)

            # Generate narration (if not agent mode)
            narration_text = None
            if adjusted_mode != "agent":
                memories_context = format_memories_for_gemini(unseen_memories[:5])
                narration_text = generate_narration(topic, memories_context, transcription, patient_id)
                print(f"💬 Narration: {narration_text}")

                # Save agent's response to conversation history
                conversation_history.add_turn(patient_id, topic, "agent", narration_text)

            return PatientQueryResponse(
                topic=topic,
                text=narration_text,
                displayMode=adjusted_mode,
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

    Returns all experiences from Snowflake (created by therapist).
    """

    with SnowflakeClient() as client:
        query = """
        SELECT title, general_context, created_at, total_memories
        FROM THERAPIST_EXPERIENCES
        ORDER BY created_at DESC
        LIMIT %s
        """

        client.cursor.execute(query, (limit,))
        results = client.cursor.fetchall()

        return {
            "status": "success",
            "total": len(results) if results else 0,
            "experiences": [
                {
                    "title": row[0],
                    "general_context": row[1],
                    "created_at": str(row[2]),
                    "total_memories": row[3]
                }
                for row in (results or [])
            ]
        }


@router.get("/session/stats")
async def get_session_stats(patient_id: str, topic: str):
    """
    **Get session statistics** - How many memories have been shown

    Example:
    ```
    GET /patient/session/stats?patient_id=patient_123&topic=disney
    ```
    """
    stats = session_manager.get_session_stats(patient_id, topic)
    return stats


@router.post("/session/reset")
async def reset_session(
    patient_id: str,
    topic: Optional[str] = None,
    reset_conversation: bool = True
):
    """
    **Reset session** - Clear shown memories and conversation history

    Example:
    ```
    POST /patient/session/reset?patient_id=patient_123&topic=disney&reset_conversation=true
    ```
    """
    session_manager.reset_session(patient_id, topic)

    if reset_conversation:
        conversation_history.reset_conversation(patient_id, topic)

    return {
        "status": "success",
        "message": f"Session reset for patient {patient_id}" + (f" topic {topic}" if topic else " (all topics)"),
        "conversation_reset": reset_conversation
    }


@router.get("/conversation/history")
async def get_conversation_history(patient_id: str, topic: str, max_turns: int = 20):
    """
    **Get conversation history** - View recent conversation

    Example:
    ```
    GET /patient/conversation/history?patient_id=patient_123&topic=disney&max_turns=10
    ```
    """
    history = conversation_history.get_history(patient_id, topic, max_turns)

    return {
        "patient_id": patient_id,
        "topic": topic,
        "total_turns": len(history),
        "conversation": [
            {
                "timestamp": turn.timestamp.isoformat(),
                "role": turn.role,
                "message": turn.message
            }
            for turn in history
        ]
    }


@router.get("/conversation/stats")
async def get_conversation_stats(patient_id: str, topic: str):
    """
    **Get conversation statistics** - Overview of conversation

    Example:
    ```
    GET /patient/conversation/stats?patient_id=patient_123&topic=disney
    ```
    """
    stats = conversation_history.get_conversation_stats(patient_id, topic)
    return stats


@router.get("/conversation/export")
async def export_conversation(patient_id: str, topic: str):
    """
    **Export conversation** - Download full conversation as JSON

    Example:
    ```
    GET /patient/conversation/export?patient_id=patient_123&topic=disney
    ```
    """
    exported = conversation_history.export_conversation(patient_id, topic)

    return {
        "patient_id": patient_id,
        "topic": topic,
        "conversation": exported
    }


@router.get("/experience/topic/{topic}")
async def get_experience_by_topic(topic: str):
    """
    **Patient Endpoint**: Get experience by topic with random non-agent display.

    Patient clicks "I want to learn about college" → Fetches matching experience
    → Returns with random display mode (4-pic, 3-pic, 5-pic, video, vertical-video)

    **Example:**
    ```
    GET /patient/experience/topic/college
    ```

    **Response:**
    ```json
    {
        "topic": "college",
        "title": "College Days Memories",
        "text": "College days were full of excitement...",
        "displayMode": "4-pic",
        "media": ["url1.jpg", "url2.jpg", "url3.jpg", "url4.jpg"]
    }
    ```
    """

    with SnowflakeClient() as client:
        # Search for experience matching topic (case-insensitive)
        query = """
        SELECT experience_data
        FROM THERAPIST_EXPERIENCES
        WHERE LOWER(title) LIKE LOWER(%s)
           OR LOWER(general_context) LIKE LOWER(%s)
        ORDER BY created_at DESC
        LIMIT 1
        """

        search_pattern = f"%{topic}%"
        client.cursor.execute(query, (search_pattern, search_pattern))
        results = client.cursor.fetchall()

        if not results or not results[0][0]:
            raise HTTPException(
                status_code=404,
                detail=f"No experience found for topic: {topic}"
            )

        # Parse experience data from JSON
        experience_data = json.loads(results[0][0]) if isinstance(results[0][0], str) else results[0][0]

        # Extract all media from all scenes
        all_media = []
        for scene in experience_data.get("scenes", []):
            for memory in scene.get("memories", []):
                all_media.append({
                    "url": memory["file_url"],
                    "type": memory["file_type"],
                    "description": memory["description"]
                })

        # Count available images to determine appropriate display mode
        images = [m["url"] for m in all_media if m["type"].lower() == "image"]
        videos = [m["url"] for m in all_media if m["type"].lower() == "video"]

        # Choose display mode based on available content
        if len(images) >= 5:
            display_mode = random.choice(["5-pic", "4-pic", "3-pic"])
        elif len(images) == 4:
            display_mode = "4-pic"
        elif len(images) == 3:
            display_mode = "3-pic"
        elif len(images) == 2:
            display_mode = "2-pic"
        elif len(images) == 1:
            display_mode = "1-pic"
        elif videos:
            display_mode = random.choice(["video", "vertical-video"])
        else:
            display_mode = "4-pic"  # Fallback

        # Select media based on chosen mode
        selected_media = []
        if display_mode in ["1-pic", "2-pic", "3-pic", "4-pic", "5-pic"]:
            count = int(display_mode.split("-")[0])
            selected_media = images[:count]
        elif display_mode in ["video", "vertical-video"]:
            selected_media = videos[:1] if videos else images[:1]

        return PatientQueryResponse(
            topic=topic,
            text=experience_data.get("overall_narrative"),
            displayMode=display_mode,
            media=selected_media
        )
