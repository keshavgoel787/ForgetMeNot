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

from api.experiences import router as therapist_router
from api.patient_query import router as patient_router
from api.patient_query_optimized import router as patient_fast_router
from api.agent_conversation import router as agent_router
from api.metadata import router as admin_metadata_router
from api.upload import router as admin_upload_router

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
    allow_origins=[
        "https://forgetmenotclient.onrender.com",
        "https://forget-me-not.tech",
        "http://localhost:5173",  # Local development
        "http://localhost:3000",  # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - Organized by Therapist → Admin → Patient → Agent
app.include_router(therapist_router)
app.include_router(patient_router)
app.include_router(patient_fast_router)  # Optimized endpoints
app.include_router(agent_router)  # Agent conversation (Avery)
app.include_router(admin_metadata_router)
app.include_router(admin_upload_router)


@app.get("/")
async def root():
    """Health check and API overview"""
    return {
        "status": "running",
        "service": "ReMind - AI Companion for Alzheimer's Care",
        "version": "2.0.0",
        "architecture": "Therapist → Admin → Patient → Agent",
        "endpoints": {
            "therapist": {
                "create_experience": "POST /therapist/create-experience - Create memory experience for patient",
                "list_experiences": "GET /therapist/experiences - List all created experiences",
                "delete_experience": "DELETE /therapist/experience/{id} - Delete an experience"
            },
            "patient": {
                "query": "POST /patient/query - Ask questions (6-mode AI response)",
                "query_test": "POST /patient/query-test - Test query without audio",
                "view_experience": "GET /patient/experience/{id} - View assigned experience",
                "list_experiences": "GET /patient/experiences - List available experiences",
                "get_by_topic": "GET /patient/experience/topic/{topic} - Get experience by topic (random non-agent display)"
            },
            "agent": {
                "talk": "POST /agent/talk - Converse with Avery (AI companion with personality & voice)",
                "profile": "GET /agent/profile/{agent_name} - Get agent profile and personality"
            },
            "admin": {
                "build_metadata": "POST /admin/metadata/build - Build metadata from GCS",
                "upload_snowflake": "POST /admin/upload/snowflake - Upload to Snowflake",
                "upload_gcs": "POST /admin/upload/gcs - Upload files to GCS"
            },
            "docs": "/docs - Interactive API documentation"
        },
        "flow": "Therapist creates experience → Patient views & interacts → Agent conversation (Avery) → Admin manages data"
    }
