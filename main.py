from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from google.cloud import speech, storage
from dotenv import load_dotenv
import os, aiofiles

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="ReMind Transcriber (Preview)")

# Your GCS bucket name
GCS_BUCKET = os.getenv("GCS_BUCKET", "forgetmenot-videos")

# Set Google credentials from .env
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Initialize Google clients
storage_client = storage.Client()
speech_client = speech.SpeechClient()

# Helper: save uploaded audio
async def save_upload_file(upload_file: UploadFile, destination: str):
    async with aiofiles.open(destination, 'wb') as out_file:
        while content := await upload_file.read(1024):
            await out_file.write(content)


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Save locally
        local_path = f"temp_{file.filename}"
        await save_upload_file(file, local_path)

        # Read audio file content
        with open(local_path, 'rb') as audio_file:
            content = audio_file.read()

        # Configure transcription with content instead of GCS URI
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            language_code="en-US",
            enable_automatic_punctuation=True,
        )

        # Run transcription
        operation = speech_client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=300)
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])

        # Clean up local file
        os.remove(local_path)

        return JSONResponse(content={
            "status": "success",
            "transcription": transcript
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
