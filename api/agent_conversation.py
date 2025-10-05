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


async def generate_agent_speech(text: str, voice_name: str) -> str:
    """Call TTS API to generate speech"""

    tts_url = "https://forgetmenot-eq7i.onrender.com/text-to-speech"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            tts_url,
            json={"text": text, "name": voice_name}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"TTS API failed: {response.text}"
            )

        # TTS API returns audio URL as string
        audio_url = response.json()
        return audio_url


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
        temp_path = f"/tmp/{audio_file.filename}"
        with open(temp_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)

        transcription = transcribe_audio_file(temp_path)
        print(f"🤖 Agent conversation started")
        print(f"   Patient said: '{transcription}'")
        print(f"   Topic: {topic}")

        # Step 2: Get agent profile
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

        # Step 4: Get conversation history
        conversation_context = conversation_history.get_formatted_history(
            patient_id, f"agent_{topic}", max_turns=5
        )

        # Step 5: Generate response with Avery's personality
        prompt = f"""You are {agent.name}, {agent.description}

Your personality: {agent.personality}

Your traits and preferences:
{json.dumps(agent.knowledge, indent=2)}

The person you're talking to just said: "{transcription}"

{f"Here are some of their memories about {topic}:" if memories else "You're having a general conversation."}
{memories_context}

Recent conversation:
{conversation_context}

INSTRUCTIONS:
- Respond as {agent.name} with your warm, empathetic personality
- If there are memories, point out specific details you see and help them reminisce
- If no specific memories, still be supportive and engage naturally
- Use "I" to refer to yourself as {agent.name}
- Keep it conversational - 2-3 sentences
- Be slightly playful but calming
- Vary your responses - don't always start the same way

Respond as {agent.name} (2-3 sentences):"""

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

        # Step 7: Save to conversation history
        conversation_history.add_turn(patient_id, f"agent_{topic}", "patient", transcription)
        conversation_history.add_turn(patient_id, f"agent_{topic}", "agent", response_text)

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
