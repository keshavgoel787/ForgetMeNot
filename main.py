"""
ReMind - AI Memory Companion API
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import time
import logging

from api.transcribe import router as transcribe_router
from api.memories import router as memories_router
from api.metadata import router as metadata_router
from api.upload import router as upload_router

# Load environment variables
load_dotenv()

# Set Google credentials from .env
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ReMind API",
    description="AI Memory Companion for Alzheimer's Care - Complete data pipeline and memory retrieval API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log incoming request
    logger.info(f"➡️  {request.method} {request.url.path} - Client: {request.client.host}")

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"⬅️  {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}s"
    )

    return response

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
