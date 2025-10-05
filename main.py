"""
ReMind - AI Memory Companion API
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from api.transcribe import router as transcribe_router
from api.memories import router as memories_router
from api.metadata import router as metadata_router
from api.upload import router as upload_router

# Load environment variables
load_dotenv()

# Set Google credentials from .env
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Initialize FastAPI app
app = FastAPI(
    title="ReMind API",
    description="AI Memory Companion for Alzheimer's Care - Complete data pipeline and memory retrieval API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcribe_router, tags=["Transcription"])
app.include_router(memories_router, tags=["Memories"])
app.include_router(metadata_router, tags=["Metadata"])
app.include_router(upload_router, tags=["Upload"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "ReMind API",
        "version": "2.0.0",
        "endpoints": {
            "memories": "/memories/search - Search and retrieve memories with AI",
            "metadata": "/metadata/build - Build metadata from GCS",
            "upload_snowflake": "/upload/snowflake - Upload metadata to Snowflake",
            "upload_gcs": "/upload/gcs - Upload files to Google Cloud Storage",
            "transcribe": "/transcribe/ - Transcribe audio files",
            "docs": "/docs - Interactive API documentation"
        }
    }
