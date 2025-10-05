"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import List, Optional


class MemoryContext(BaseModel):
    """Memory analysis context from Gemini"""
    people: Optional[List[str]] = []
    location: Optional[str] = None
    event: Optional[str] = None
    emotion: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[str] = None


class TranscriptionResponse(BaseModel):
    """Response from transcription endpoint"""
    status: str
    transcript: str
    context: MemoryContext
