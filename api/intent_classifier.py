"""
Intent Classification for Patient Requests

Classifies patient audio requests into 6 display modes:
1. 4-pic: 4 images + narration text
2. 3-pic: 3 images + narration text
3. video: Single horizontal video + narration text
4. 5-pic: 5 images + narration text
5. vertical-video: Single vertical video + narration text
6. agent: Conversational mode - lip-sync video (no text)
"""

from typing import Dict, Tuple, List
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from scripts.lib.gemini_client import generate_text
from scripts.lib.snowflake_client import SnowflakeClient


def classify_intent_and_media(
    transcription: str,
    topic: str,
    client: SnowflakeClient
) -> Tuple[str, Dict]:
    """
    Classify patient request into display mode based on:
    1. Intent from transcription (what patient wants to do)
    2. Available media in Snowflake (what we have for this topic)

    Args:
        transcription: Transcribed text from user audio
        topic: Topic/person/event name
        client: Connected SnowflakeClient

    Returns:
        Tuple of (display_mode, media_info)
        - display_mode: One of [4-pic, 3-pic, video, 5-pic, vertical-video, agent]
        - media_info: Dict with available media details
    """

    # Step 1: Classify intent using Gemini
    intent = classify_intent_with_gemini(transcription, topic)

    # Step 2: Check available media in Snowflake
    media_availability = get_media_availability(topic, client)

    # Step 3: Determine display mode based on intent + availability
    display_mode = determine_display_mode(intent, media_availability)

    return display_mode, media_availability


def classify_intent_with_gemini(transcription: str, topic: str) -> Dict:
    """
    Use Gemini to classify the intent of the patient's request.

    Returns:
        Dict with:
        - intent_type: "memory_replay" or "conversation"
        - interaction_style: "passive" or "interactive"
        - emotional_tone: "nostalgic", "curious", "seeking_connection", "confused"
        - specific_request: What exactly the patient wants
        - confidence: 0-1 score
    """

    prompt = f"""You are an AI assistant helping Alzheimer's patients interact with their memories. Your task is to deeply analyze the patient's request and classify their intent with high precision.

**PATIENT REQUEST:**
Transcription: "{transcription}"
Topic/Person/Event: "{topic}"

**YOUR TASK:**
Analyze this request across multiple dimensions to understand what the patient truly wants:

1. **Intent Type** (Choose ONE):
   - "memory_replay" = Patient wants to passively experience memories
     Examples:
     • "Show me the beach day"
     • "I want to learn more about the beach day and when we got ice cream"
     • "Tell me what happened at Disney"
     • "Play memories of Avery"
     • "What did we do at the football game?"

   - "conversation" = Patient wants active dialogue/interaction with a person
     Examples:
     • "I want to talk to Avery"
     • "Can I speak with Avery about what we did?"
     • "Let me chat with mom about the trip"
     • "I want to ask Avery about the beach"

2. **Interaction Style** (Choose ONE):
   - "passive" = Patient wants to watch/listen to memories (one-way experience)
     Indicators: "show", "play", "see", "watch", "tell me about", "what happened"

   - "interactive" = Patient wants two-way conversation/dialogue
     Indicators: "talk to", "speak with", "chat with", "ask", "discuss with"

3. **Emotional Tone** (Choose ONE that best fits):
   - "nostalgic" = Wanting to relive happy moments warmly
   - "curious" = Seeking information/details about past events
   - "seeking_connection" = Wanting to feel close to a person
   - "confused" = Uncertain about what happened or who was there

4. **Specific Request** (Extract in your own words):
   - What exactly is the patient asking for? Be specific.
   - Examples: "wants to see ice cream moment from beach day", "wants to talk to Avery about beach activities"

5. **Confidence Score** (0.0 to 1.0):
   - How confident are you in this classification?
   - 0.9-1.0 = Very clear intent
   - 0.7-0.9 = Clear intent with minor ambiguity
   - 0.5-0.7 = Somewhat ambiguous
   - 0.0-0.5 = Very ambiguous

**IMPORTANT CLASSIFICATION RULES:**
- If the patient explicitly mentions wanting to "talk to", "speak with", or "chat with" a PERSON → intent_type = "conversation"
- If the patient asks questions ABOUT memories but doesn't request direct conversation → intent_type = "memory_replay"
- "I want to talk to Avery about X" = conversation (they want dialogue)
- "Tell me about what Avery and I did" = memory_replay (they want information)

**OUTPUT FORMAT (respond ONLY with valid JSON):**
{{
  "intent_type": "memory_replay" or "conversation",
  "interaction_style": "passive" or "interactive",
  "emotional_tone": "nostalgic" or "curious" or "seeking_connection" or "confused",
  "specific_request": "detailed description here",
  "confidence": 0.0-1.0
}}

**RESPOND NOW WITH ONLY THE JSON:**"""

    try:
        response = generate_text(
            prompt,
            model_name="gemini-2.5-flash",
            temperature=0.3,
            max_tokens=200
        )

        # Parse JSON response
        import json
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()

        intent_data = json.loads(response)
        return intent_data

    except Exception as e:
        print(f"⚠️ Error classifying intent: {e}")
        # Default to memory replay if classification fails
        return {
            "intent_type": "memory_replay",
            "interaction_style": "passive",
            "emotional_tone": "curious",
            "specific_request": f"wants to learn about {topic}",
            "confidence": 0.5
        }


def get_media_availability(topic: str, client: SnowflakeClient) -> Dict:
    """
    Query Snowflake to check available media for the topic.

    Returns:
        Dict with:
        - total_images: count
        - total_videos: count
        - video_orientations: {"horizontal": count, "vertical": count}
        - sample_media: List of file URLs
    """

    # Search for media related to topic
    client.cursor.execute("""
        SELECT
            file_type,
            file_url,
            description,
            VECTOR_COSINE_SIMILARITY(
                embedding,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s)
            ) AS similarity
        FROM MEMORY_VAULT
        WHERE description IS NOT NULL AND description != ''
        ORDER BY similarity DESC
        LIMIT 20
    """, (topic,))

    results = client.cursor.fetchall()

    images = []
    horizontal_videos = []
    vertical_videos = []

    for file_type, file_url, description, similarity in results:
        if similarity < 0.5:  # Only include relevant matches
            continue

        if file_type.lower() == 'image':
            images.append(file_url)
        elif file_type.lower() == 'video':
            # Simple heuristic: check if "vertical" or "portrait" in description
            # In production, you'd check actual video dimensions
            if 'vertical' in description.lower() or 'portrait' in description.lower():
                vertical_videos.append(file_url)
            else:
                horizontal_videos.append(file_url)

    return {
        "total_images": len(images),
        "total_videos": len(horizontal_videos) + len(vertical_videos),
        "video_orientations": {
            "horizontal": len(horizontal_videos),
            "vertical": len(vertical_videos)
        },
        "images": images[:10],  # Limit to top 10
        "horizontal_videos": horizontal_videos[:5],
        "vertical_videos": vertical_videos[:5],
        "has_enough_media": len(images) + len(horizontal_videos) + len(vertical_videos) >= 3
    }


def determine_display_mode(intent: Dict, media_availability: Dict) -> str:
    """
    Determine display mode based on intent and available media.

    Priority Logic:
    1. If intent = "conversation" → agent mode
    2. If intent = "memory_replay":
       - Prefer videos if available
       - Otherwise, use images (choose pic count based on availability)
    """

    # Agent mode if conversation intent
    if intent.get("intent_type") == "conversation" or intent.get("interaction_style") == "interactive":
        return "agent"

    # Memory replay mode - choose based on available media
    has_vertical_video = media_availability["video_orientations"]["vertical"] > 0
    has_horizontal_video = media_availability["video_orientations"]["horizontal"] > 0
    total_images = media_availability["total_images"]

    # Priority 1: Vertical video (more engaging for mobile)
    if has_vertical_video:
        return "vertical-video"

    # Priority 2: Horizontal video
    if has_horizontal_video:
        return "video"

    # Priority 3: Images - choose count based on availability
    if total_images >= 5:
        return "5-pic"
    elif total_images >= 4:
        return "4-pic"
    elif total_images >= 3:
        return "3-pic"

    # Fallback: Use whatever we have
    if total_images >= 1:
        return "3-pic"  # Show what we have

    # Last resort: agent mode (can talk about memories even without media)
    return "agent"


def classify_request(transcription: str, topic: str) -> Tuple[str, Dict]:
    """
    Main entry point for intent classification.

    Args:
        transcription: Transcribed audio text
        topic: Topic/person/event name

    Returns:
        Tuple of (display_mode, debug_info)
    """
    with SnowflakeClient() as client:
        display_mode, media_info = classify_intent_and_media(transcription, topic, client)

        debug_info = {
            "transcription": transcription,
            "topic": topic,
            "display_mode": display_mode,
            "media_availability": media_info
        }

        return display_mode, debug_info
