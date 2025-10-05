"""
Experience Request API
Therapist creates memory experience, patient receives the result
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from scripts.lib.snowflake_client import SnowflakeClient
from scripts.retrieval_cycle import search_memories_by_query, generate_answer_with_gemini, format_memories_for_gemini
from api.schemas import MemoryResult

# In-memory storage for experiences (use Redis/DB in production)
experiences = {}

router = APIRouter(prefix="/experiences", tags=["Memory Experiences"])


class CreateExperienceRequest(BaseModel):
    """Therapist creates an experience"""
    title: str = Field(..., description="Experience title (e.g., 'Day at the Beach')")
    general_context: str = Field(..., description="General context (e.g., 'me and Anna at the beach')")
    scenes: List[str] = Field(..., description="Specific scenes to find (e.g., ['holding hands', 'eating ice cream'])")
    top_k: int = Field(default=3, ge=1, le=10, description="Memories per scene")


class SceneResult(BaseModel):
    """Memories for a specific scene"""
    scene: str
    memories: List[MemoryResult]
    ai_narrative: str


class ExperienceResponse(BaseModel):
    """Complete experience result"""
    experience_id: str
    title: str
    general_context: str
    scenes: List[SceneResult]
    overall_narrative: str
    total_memories: int
    created_at: str
    patient_url: str


@router.post("/create", response_model=ExperienceResponse)
async def create_experience(request: CreateExperienceRequest):
    """
    **Therapist Endpoint**: Create a memory experience.

    The therapist submits an experience request with title, context, and scenes.
    The system searches for memories, generates AI narratives, and returns everything.

    **Example Request:**
    ```json
    {
      "title": "Day at the Beach with Anna",
      "general_context": "me and Anna at the beach",
      "scenes": [
        "holding hands on the beach",
        "eating ice cream together",
        "playing in the sand"
      ],
      "top_k": 3
    }
    ```

    **Returns:**
    - `experience_id`: Unique ID to access the experience
    - `patient_url`: URL patient uses to view the experience
    - Complete memory results with AI narratives
    """

    experience_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    with SnowflakeClient() as client:
        scene_results = []
        total_memories = 0

        # Search for each scene
        for scene in request.scenes:
            # Combine general context with scene for better search
            query = f"{request.general_context} - {scene}"

            # Search memories
            memories = search_memories_by_query(query, client, top_k=request.top_k)

            if not memories:
                continue

            total_memories += len(memories)

            # Format memories
            memory_results = []
            for memory in memories:
                event_name, file_name, file_type, description, people, event_summary, file_url, similarity = memory

                people_list = [p.strip() for p in people.split(',') if p and p.strip()] if people else []

                memory_results.append(MemoryResult(
                    event_name=event_name,
                    file_name=file_name,
                    file_type=file_type,
                    description=description,
                    people=people_list,
                    event_summary=event_summary,
                    file_url=file_url,
                    similarity=float(similarity)
                ))

            # Generate AI narrative for this scene
            memories_context = format_memories_for_gemini(memories)
            scene_narrative = generate_answer_with_gemini(
                f"{request.general_context} - {scene}",
                memories_context,
                memories
            )

            scene_results.append(SceneResult(
                scene=scene,
                memories=memory_results,
                ai_narrative=scene_narrative
            ))

        if not scene_results:
            raise HTTPException(
                status_code=404,
                detail=f"No memories found for '{request.general_context}'"
            )

        # Generate overall narrative combining all scenes
        all_narratives = "\n".join([s.ai_narrative for s in scene_results])
        overall_narrative = f"Here are your memories about {request.title}:\n\n{all_narratives}"

        # Store experience
        experience_data = {
            "experience_id": experience_id,
            "title": request.title,
            "general_context": request.general_context,
            "scenes": [s.dict() for s in scene_results],
            "overall_narrative": overall_narrative,
            "total_memories": total_memories,
            "created_at": timestamp
        }

        experiences[experience_id] = experience_data

        return ExperienceResponse(
            experience_id=experience_id,
            title=request.title,
            general_context=request.general_context,
            scenes=scene_results,
            overall_narrative=overall_narrative,
            total_memories=total_memories,
            created_at=timestamp,
            patient_url=f"/experiences/view/{experience_id}"
        )


@router.get("/view/{experience_id}")
async def view_experience(experience_id: str):
    """
    **Patient Endpoint**: View an experience by ID.

    The patient accesses this URL to see their memory experience.
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


@router.get("/list")
async def list_experiences(limit: int = 10):
    """
    List recent experiences.

    **Query Params:**
    - `limit`: Maximum number of experiences to return (default: 10)
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
                "total_memories": exp["total_memories"],
                "patient_url": f"/experiences/view/{exp['experience_id']}"
            }
            for exp in reversed(recent)
        ]
    }


@router.delete("/{experience_id}")
async def delete_experience(experience_id: str):
    """Delete an experience"""

    if experience_id not in experiences:
        raise HTTPException(
            status_code=404,
            detail=f"Experience {experience_id} not found"
        )

    del experiences[experience_id]

    return {
        "status": "success",
        "message": f"Experience {experience_id} deleted"
    }
