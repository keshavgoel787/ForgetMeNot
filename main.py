"""
ReMind - AI Memory Companion API
Main application entry point
"""
from fastapi import FastAPI
from dotenv import load_dotenv
import os

from api.transcribe import router as transcribe_router

# Load environment variables
load_dotenv()

# Set Google credentials from .env
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Initialize FastAPI app
app = FastAPI(
    title="ReMind API",
    description="AI Memory Companion for Alzheimer's Care",
    version="1.0.0"
)

# Include routers
app.include_router(transcribe_router, tags=["Transcription"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "ReMind API",
        "version": "1.0.0"
    }
