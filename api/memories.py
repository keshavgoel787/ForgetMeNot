"""
Memory Search and Retrieval API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from scripts.lib.snowflake_client import SnowflakeClient
from scripts.lib.config import Config
from scripts.retrieval_cycle import (
    search_memories_by_query,
    format_memories_for_gemini,
    generate_answer_with_gemini
)
from api.schemas import SearchQuery, RetrievalResponse, MemoryResult, ErrorResponse

router = APIRouter(prefix="/memories", tags=["Memories"])


@router.post("/search", response_model=RetrievalResponse)
async def search_and_retrieve(search_request: SearchQuery):
    """
    Search memories and generate AI-powered answer.

    This endpoint performs the complete retrieval cycle:
    1. Converts query to embedding
    2. Searches Snowflake using vector similarity
    3. Uses Gemini to synthesize natural language answer

    **Example queries:**
    - "What did we eat at Disney?"
    - "Tell me about the ski trip"
    - "Who was at the football game?"
    """
    try:
        with SnowflakeClient() as client:
            # Step 1: Search for relevant memories
            memories = search_memories_by_query(
                search_request.query,
                client,
                top_k=search_request.top_k
            )

            if not memories:
                return RetrievalResponse(
                    answer="I couldn't find any memories matching your question.",
                    memories=[],
                    query=search_request.query,
                    model_used="none"
                )

            # Step 2: Format memories for Gemini
            memories_context = format_memories_for_gemini(memories)

            # Step 3: Generate natural language answer
            answer = generate_answer_with_gemini(search_request.query, memories_context, memories)

            # Step 4: Format response
            memory_results = []
            if search_request.show_sources:
                for memory in memories:
                    event_name, file_name, file_type, description, people, event_summary, file_url, similarity = memory

                    # Format people array - handle comma-separated string from Snowflake
                    people_list = []
                    if people and isinstance(people, str):
                        # Split by comma and filter empty values
                        people_list = [p.strip() for p in people.split(',') if p and p.strip()]

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

            return RetrievalResponse(
                answer=answer,
                memories=memory_results,
                query=search_request.query,
                model_used="gemini-2.5-flash"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search", response_model=RetrievalResponse)
async def search_and_retrieve_get(
    query: str = Query(..., description="Natural language query to search memories"),
    top_k: int = Query(default=5, ge=1, le=20, description="Number of results to retrieve"),
    show_sources: bool = Query(default=True, description="Include source memories in response")
):
    """
    Search memories using GET request (alternative to POST).

    **Example:**
    - GET /memories/search?query=What did we eat at Disney?&top_k=5
    """
    search_request = SearchQuery(query=query, top_k=top_k, show_sources=show_sources)
    return await search_and_retrieve(search_request)


@router.get("/health")
async def health_check():
    """Check if memory service can connect to Snowflake"""
    try:
        with SnowflakeClient() as client:
            client.cursor.execute("SELECT COUNT(*) FROM MEMORY_VAULT")
            count = client.cursor.fetchone()[0]
            return {
                "status": "healthy",
                "snowflake_connected": True,
                "total_memories": count
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "snowflake_connected": False,
            "error": str(e)
        }
