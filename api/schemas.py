"""
Pydantic models for ReMind API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ============================================================================
# Memory Search & Retrieval Schemas
# ============================================================================

class SearchQuery(BaseModel):
    """Request model for memory search"""
    query: str = Field(..., description="Natural language query to search memories")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to retrieve")
    show_sources: bool = Field(default=True, description="Include source memories in response")


class MemoryResult(BaseModel):
    """Single memory search result"""
    event_name: str
    file_name: str
    file_type: str
    description: str
    people: List[str]
    event_summary: str
    file_url: str
    similarity: float


class RetrievalResponse(BaseModel):
    """Response model for retrieval cycle"""
    model_config = {"protected_namespaces": ()}

    status: str = Field(default="success")
    answer: str = Field(..., description="AI-generated natural language answer")
    memories: List[MemoryResult] = Field(default=[], description="Source memories used for answer")
    query: str = Field(..., description="Original user query")
    model_used: str = Field(default="gemini-2.5-flash", description="AI model used for generation")


# ============================================================================
# Therapist Prompt & AI Memory Generation Schemas
# ============================================================================

class TherapistPrompt(BaseModel):
    """Therapist's memory recreation prompt"""
    patient_id: Optional[str] = Field(default=None, description="Patient identifier")
    general_description: str = Field(..., description="General memory description (e.g., 'me and Anna at the beach')")
    specific_scenes: List[str] = Field(..., description="Specific scene descriptions (e.g., ['holding hands', 'eating ice cream'])")
    top_k_per_scene: int = Field(default=3, ge=1, le=10, description="Number of memories to retrieve per scene")


class SceneMemories(BaseModel):
    """Memories for a specific scene"""
    scene_description: str
    memories: List[MemoryResult]
    ai_narrative: str = Field(..., description="AI-generated narrative for this scene")


class AIMemoryResponse(BaseModel):
    """Complete AI-generated memory response"""
    model_config = {"protected_namespaces": ()}

    status: str = Field(default="success")
    patient_id: Optional[str] = None
    general_description: str
    scenes: List[SceneMemories] = Field(..., description="Memories and narratives for each scene")
    overall_narrative: str = Field(..., description="Complete AI-generated memory story")
    total_memories_found: int
    session_id: str = Field(..., description="Unique session identifier for tracking")
    model_used: str = Field(default="gemini-2.5-flash")


# ============================================================================
# GCS Metadata Building Schemas
# ============================================================================

class MetadataRow(BaseModel):
    """Single metadata row from GCS"""
    event_name: str
    file_name: str
    file_type: str
    description: str
    people: List[str]
    event_summary: str
    file_url: str


class BuildMetadataResponse(BaseModel):
    """Response for metadata building operation"""
    status: str
    rows_generated: int
    metadata: List[MetadataRow]
    csv_path: str
    message: str


# ============================================================================
# Snowflake Upload Schemas
# ============================================================================

class UploadMetadataRequest(BaseModel):
    """Request to upload metadata to Snowflake"""
    csv_path: Optional[str] = Field(default="data/metadata.csv", description="Path to metadata CSV file")
    truncate_existing: bool = Field(default=True, description="Clear existing data before upload")


class UploadMetadataResponse(BaseModel):
    """Response for Snowflake upload operation"""
    status: str
    records_uploaded: int
    records_skipped: int
    total_records: int
    message: str


# ============================================================================
# File Upload Schemas
# ============================================================================

class FileUploadResponse(BaseModel):
    """Response for file upload to GCS"""
    status: str
    file_url: str
    bucket: str
    blob_name: str
    event_name: str
    file_type: str
    message: str


# ============================================================================
# Health Check Schemas
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    snowflake_connected: bool
    gcs_connected: bool


# ============================================================================
# Error Response Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    error: str
    detail: Optional[str] = None
