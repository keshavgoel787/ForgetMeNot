"""
Agent Conversation API - Talk with Avery (AI Memory Companion)

This endpoint enables conversational interaction with an AI agent (Avery)
who helps patients reminisce about memories in a natural, empathetic way.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Any
import sys
import os
import httpx
import json

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from scripts.lib.snowflake_client import SnowflakeClient
from scripts.lib.gemini_client import generate_text
from scripts.retrieval_cycle import search_memories_by_query, format_memories_for_gemini
from api.conversation_history import conversation_history
from api.patient_query import transcribe_audio_file

router = APIRouter(prefix="/agent", tags=["Agent Conversation"])


class AgentProfile(BaseModel):
    """Agent personality profile"""
    id: str
    name: str
    description: str
    voice_name: str
    personality: str
    knowledge: Dict[str, Any]


class AgentResponse(BaseModel):
    """Agent conversation response"""
    agent_name: str
    text: str
    audio_url: str
    personality_note: str


def get_agent_profile(agent_name: str = "Avery") -> AgentProfile:
    """Fetch agent profile from Snowflake"""

    with SnowflakeClient() as client:
        query = """
        SELECT id, name, description, voice_name, personality, knowledge
        FROM AGENT_PROFILES
        WHERE name = %s
        LIMIT 1
        """

        client.cursor.execute(query, (agent_name,))
        result = client.cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Agent profile '{agent_name}' not found"
            )

        agent_id, name, description, voice_name, personality, knowledge = result

        # Parse knowledge JSON
        knowledge_dict = json.loads(knowledge) if isinstance(knowledge, str) else knowledge

        return AgentProfile(
            id=agent_id,
            name=name,
            description=description,
            voice_name=voice_name,
            personality=personality,
            knowledge=knowledge_dict
        )


def detect_agent_from_text(text: str) -> str:
    """Detect which agent the user wants to talk to from transcribed text"""
    text_lower = text.lower()

    # Check for explicit agent mentions
    if "tyler" in text_lower:
        return "Tyler"
    elif "avery" in text_lower:
        return "Avery"

    # Default to Avery
    return "Avery"


async def generate_agent_speech(text: str, voice_name: str) -> str:
    """Call TTS API to generate speech and upload to GCS"""

    # Use environment variable for TTS URL, default to deployed API
    tts_url = os.getenv("TTS_API_URL", "https://forgetmenot-eq7i.onrender.com/text-to-speech")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            tts_url,
            json={"text": text, "name": voice_name}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"TTS API failed: {response.status_code}"
            )

        # TTS API returns binary MP3 audio
        # Upload to GCS and return public URL
        from google.cloud import storage
        import time

        bucket_name = os.getenv("GCS_BUCKET", "forgetmenot-videos")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        # Create unique filename
        timestamp = int(time.time() * 1000)
        filename = f"agent_audio/{voice_name}_{timestamp}.mp3"
        blob = bucket.blob(filename)

        # Upload binary audio content
        blob.upload_from_string(response.content, content_type="audio/mpeg")

        # Generate signed URL (valid for 1 hour)
        from datetime import timedelta
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=1),
            method="GET"
        )

        return signed_url


@router.post("/talk", response_model=AgentResponse)
async def talk_to_agent(
    audio_file: UploadFile = File(..., description="MP3 audio file from patient"),
    topic: str = Form(default="general", description="Conversation topic"),
    patient_id: str = Form(default="default_patient", description="Patient ID"),
    agent_name: str = Form(default="Avery", description="Agent name (default: Avery)")
):
    """
    **Agent Conversation Endpoint** - Talk to Avery with Audio

    Upload audio, Avery responds with her personality and voice.

    **Flow:**
    1. Transcribe patient's audio
    2. Retrieve agent profile (Avery) from Snowflake
    3. Search for relevant memories based on topic
    4. Generate conversational response using Gemini (with Avery's personality)
    5. Convert response to speech using TTS API (Avery's voice)
    6. Return both text and audio

    **Example Request:**
    ```bash
    POST /agent/talk
    Form Data:
    - audio_file: <patient_audio.mp3>
    - topic: "beach"
    - patient_id: "patient_123"
    ```

    **Example Response:**
    ```json
    {
      "agent_name": "Avery",
      "text": "Oh, I love talking about the beach! Let me show you...",
      "audio_url": "https://storage.googleapis.com/.../avery_response.mp3",
      "personality_note": "Warm, empathetic, humorous"
    }
    ```
    """

    temp_path = None
    try:
        # Step 1: Save and transcribe audio
        import time
        temp_path = f"/tmp/agent_{int(time.time())}_{audio_file.filename}"
        with open(temp_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)

        print(f"🤖 Agent conversation started")
        print(f"   Audio saved to: {temp_path}")

        transcription = transcribe_audio_file(temp_path)
        print(f"   Patient said: '{transcription}'")
        print(f"   Topic: {topic}")

        # Step 2: Detect which agent to use from transcription
        detected_agent = detect_agent_from_text(transcription)
        # Override with detected agent if different
        if detected_agent != agent_name:
            print(f"   🔍 Detected agent: {detected_agent} (overriding default: {agent_name})")
            agent_name = detected_agent

        # Step 3: Get agent profile
        agent = get_agent_profile(agent_name)
        print(f"   Agent: {agent.name} ({agent.voice_name})")

        # Step 3: Retrieve relevant memories
        with SnowflakeClient() as client:
            memories = search_memories_by_query(topic, client, top_k=5)

        memories_context = ""
        if memories:
            memories_context = format_memories_for_gemini(memories)
            print(f"   Found {len(memories)} relevant memories")
        else:
            print(f"   No specific memories found - general conversation")

        # Step 4: Get conversation history (per agent)
        conversation_context = conversation_history.get_formatted_history(
            patient_id, f"agent_{agent.name.lower()}", max_turns=5
        )

        # Step 5: Generate response with agent's personality
        prompt = f"""You are {agent.name}, {agent.description}

Your personality: {agent.personality}

Your traits and preferences:
{json.dumps(agent.knowledge, indent=2)}

The person you're talking to just said: "{transcription}"

{f"Here are YOUR memories and experiences about {topic} that you want to share with them:" if memories else "You're having a general conversation."}
{memories_context}

Recent conversation:
{conversation_context}

INSTRUCTIONS:
- You're {agent.name}, sharing YOUR OWN experiences and memories with the person
- The memories shown above are YOUR memories - talk about them as if YOU experienced them
- Use "I" when talking about these experiences (e.g., "I remember when I went to Disney..." or "I had so much fun at the beach...")
- Be conversational and personal - you're sharing your life with them
- Reference specific details from YOUR memories naturally
- Keep it to 2-3 sentences
- Match your personality: {agent.personality}
- Vary your responses - don't always start the same way

Respond as {agent.name} sharing your own experiences (2-3 sentences):"""

        response_text = generate_text(
            prompt,
            model_name="gemini-2.5-flash",
            temperature=0.9,
            max_tokens=150
        )

        print(f"   💬 {agent.name}: {response_text}")

        # Step 6: Generate speech with agent's voice
        audio_url = await generate_agent_speech(response_text, agent.voice_name)
        print(f"   🔊 Audio generated: {audio_url}")

        # Step 7: Save to conversation history (per agent)
        conversation_history.add_turn(patient_id, f"agent_{agent.name.lower()}", "patient", transcription)
        conversation_history.add_turn(patient_id, f"agent_{agent.name.lower()}", "agent", response_text)

        return AgentResponse(
            agent_name=agent.name,
            text=response_text,
            audio_url=audio_url,
            personality_note=agent.personality
        )

    except Exception as e:
        print(f"❌ Agent conversation error: {e}")
        raise HTTPException(status_code=500, detail=f"Agent conversation failed: {str(e)}")

    finally:
        # Cleanup temporary audio file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/talk/avery", response_model=AgentResponse)
async def talk_to_avery(
    audio_file: UploadFile = File(..., description="MP3 audio file from patient"),
    topic: str = Form(default="general", description="Conversation topic"),
    patient_id: str = Form(default="default_patient", description="Patient ID")
):
    """
    **Talk to Avery** - Direct route for Avery conversations

    Click on Avery's portrait to start chatting with her warm, empathetic personality.
    """
    # Call the main talk endpoint with agent_name fixed to "Avery"
    return await talk_to_agent(audio_file, topic, patient_id, agent_name="Avery")


@router.post("/talk/tyler", response_model=AgentResponse)
async def talk_to_tyler(
    audio_file: UploadFile = File(..., description="MP3 audio file from patient"),
    topic: str = Form(default="general", description="Conversation topic"),
    patient_id: str = Form(default="default_patient", description="Patient ID")
):
    """
    **Talk to Tyler** - Direct route for Tyler conversations

    Click on Tyler's portrait to start chatting with his energetic, adventurous personality.
    """
    # Call the main talk endpoint with agent_name fixed to "Tyler"
    return await talk_to_agent(audio_file, topic, patient_id, agent_name="Tyler")


@router.get("/profile/{agent_name}")
async def get_agent_info(agent_name: str = "Avery"):
    """
    **Get Agent Profile** - View agent details

    Returns agent personality, voice, and knowledge base.

    Example: `GET /agent/profile/Avery`
    """

    try:
        agent = get_agent_profile(agent_name)
        return {
            "name": agent.name,
            "description": agent.description,
            "voice": agent.voice_name,
            "personality": agent.personality,
            "knowledge": agent.knowledge
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
