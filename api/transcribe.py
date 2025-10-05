"""
Transcription API routes
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
import aiofiles
import os

from services.speech_service import SpeechService
from services.gemini_service import GeminiService
from models.schemas import TranscriptionResponse, MemoryContext


router = APIRouter()

# Initialize services
speech_service = SpeechService()
gemini_service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))


async def save_upload_file(upload_file: UploadFile, destination: str):
    """Helper to save uploaded file"""
    async with aiofiles.open(destination, 'wb') as out_file:
        while content := await upload_file.read(1024):
            await out_file.write(content)


@router.post("/transcribe/", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file and analyze with Gemini.

    - **file**: Audio file (WAV, MP3, FLAC, etc.)

    Returns transcription and memory context analysis.
    """
    try:
        # Save uploaded file temporarily
        local_path = f"temp_{file.filename}"
        await save_upload_file(file, local_path)

        # Read audio content
        with open(local_path, 'rb') as audio_file:
            content = audio_file.read()

        # Transcribe audio
        transcript = speech_service.transcribe_audio(content)

        # Analyze memory with Gemini
        context_dict = gemini_service.analyze_memory(transcript)
        context = MemoryContext(**context_dict)

        # Clean up temporary file
        os.remove(local_path)

        return TranscriptionResponse(
            status="success",
            transcript=transcript,
            context=context
        )

    except Exception as e:
        # Clean up on error
        if os.path.exists(local_path):
            os.remove(local_path)
        raise HTTPException(status_code=500, detail=str(e))
