"""
Transcription API routes
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
import aiofiles
import os

router = APIRouter()

# Initialize services lazily to avoid import errors
speech_service = None
gemini_service = None

def get_services():
    """Lazy load services to avoid startup errors"""
    global speech_service, gemini_service
    if speech_service is None:
        try:
            from services.speech_service import SpeechService
            from services.gemini_service import GeminiService
            from models.schemas import TranscriptionResponse, MemoryContext
            speech_service = SpeechService()
            gemini_service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Transcription services not available: {str(e)}"
            )
    return speech_service, gemini_service


async def save_upload_file(upload_file: UploadFile, destination: str):
    """Helper to save uploaded file"""
    async with aiofiles.open(destination, 'wb') as out_file:
        while content := await upload_file.read(1024):
            await out_file.write(content)


@router.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file and analyze with Gemini.

    - **file**: Audio file (WAV, MP3, FLAC, etc.)

    Returns transcription and memory context analysis.
    """
    from models.schemas import TranscriptionResponse, MemoryContext

    # Get services (will raise 503 if not available)
    speech_svc, gemini_svc = get_services()

    local_path = None
    try:
        # Save uploaded file temporarily
        local_path = f"temp_{file.filename}"
        await save_upload_file(file, local_path)

        # Read audio content
        with open(local_path, 'rb') as audio_file:
            content = audio_file.read()

        # Transcribe audio
        transcript = speech_svc.transcribe_audio(content)

        # Analyze memory with Gemini
        context_dict = gemini_svc.analyze_memory(transcript)
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
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
        raise HTTPException(status_code=500, detail=str(e))
