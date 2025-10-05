"""
FastAPI server for ForgetMeNot processing pipeline
Endpoints:
1. POST /extract-faces - Upload data folder, extract faces, return 16 samples per person
2. POST /generate-context - Upload names.json, run name conversion + context generation
3. POST /text-to-speech - Generate speech in a person's voice
4. GET /voices - List all available voice clones
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import shutil
import json
import random
import os
import zipfile
import io
import requests
from pathlib import Path
from dotenv import load_dotenv

# Lazy imports for heavy dependencies (only needed for face extraction endpoints)
# These are imported inside the endpoint functions to avoid errors when deploying
# to environments without opencv, face_recognition, etc.
# from memory_to_people import MemoryPeopleExtractor
# from edit_pictures_based_on_json import PeopleFolderEditor
# from text_context_per_memory import MemoryContextAnalyzer

# Load environment variables
load_dotenv()

app = FastAPI(title="ForgetMeNot API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary working directory
WORK_DIR = Path("temp_processing")
WORK_DIR.mkdir(exist_ok=True)

def cleanup_temp_files(session_id: str):
    """Clean up temporary files for a session"""
    session_dir = WORK_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)

def sample_faces_from_folder(person_folder: Path, sample_size: int = 16) -> List[Path]:
    """Randomly sample N face images from a person folder"""
    face_files = list(person_folder.glob("face_*.jpg"))
    
    if len(face_files) <= sample_size:
        return face_files
    
    return random.sample(face_files, sample_size)

def create_sampled_people_zip(people_path: Path, output_zip: Path):
    """Create a zip with 16 random samples from each person folder"""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add each person folder with sampled faces
        for person_folder in people_path.iterdir():
            if person_folder.is_dir() and person_folder.name.startswith('person_'):
                person_name = person_folder.name
                
                # Sample 16 faces
                sampled_faces = sample_faces_from_folder(person_folder, sample_size=16)
                
                # Add to zip
                for face_file in sampled_faces:
                    arcname = f"people/{person_name}/{face_file.name}"
                    zipf.write(face_file, arcname=arcname)
                
                # Add metadata if exists
                metadata_file = person_folder / "metadata.json"
                if metadata_file.exists():
                    arcname = f"people/{person_name}/metadata.json"
                    zipf.write(metadata_file, arcname=arcname)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "ForgetMeNot API",
        "version": "1.0.0"
    }

@app.post("/extract-faces")
async def extract_faces(data_zip: UploadFile = File(...)):
    """
    Endpoint 1: Extract faces from uploaded data folder
    
    Input: ZIP file containing 'memories' folder with videos/images
    Output: ZIP file with person_1, person_2, etc. folders (16 samples each)
    
    Steps:
    1. Extract uploaded data
    2. Run face extraction
    3. Cluster faces into person_X folders
    4. Sample 16 random faces per person
    5. Return as ZIP
    """
    # Import heavy dependencies only when this endpoint is called
    try:
        from memory_to_people import MemoryPeopleExtractor
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Face extraction not available. This endpoint requires opencv and face_recognition libraries."
        )
    
    session_id = f"session_{os.urandom(8).hex()}"
    session_dir = WORK_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"📦 Processing session: {session_id}")
        
        # Step 1: Save and extract uploaded ZIP
        data_zip_path = session_dir / "data.zip"
        with open(data_zip_path, "wb") as f:
            content = await data_zip.read()
            f.write(content)
        
        print("📂 Extracting uploaded data...")
        extract_dir = session_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(data_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find memories folder
        memories_path = extract_dir / "memories"
        if not memories_path.exists():
            # Try to find it in subdirectories
            for item in extract_dir.rglob("memories"):
                if item.is_dir():
                    memories_path = item
                    break
        
        if not memories_path.exists():
            raise HTTPException(
                status_code=400,
                detail="No 'memories' folder found in uploaded ZIP"
            )
        
        print(f"✅ Found memories folder: {memories_path}")
        
        # Step 2: Extract faces
        print("🔍 Extracting faces...")
        people_output = session_dir / "people"
        people_output.mkdir(exist_ok=True)
        
        extractor = MemoryPeopleExtractor(str(memories_path), str(people_output))
        extractor.process_all_memories()
        
        print(f"✅ Face extraction complete")
        
        # Step 3: Create sampled ZIP
        print("📦 Creating sampled people ZIP (16 faces per person)...")
        output_zip_path = session_dir / "people_sampled.zip"
        create_sampled_people_zip(people_output, output_zip_path)
        
        print(f"✅ Session {session_id} complete")
        
        # Return ZIP file
        return FileResponse(
            path=str(output_zip_path),
            media_type="application/zip",
            filename="people_sampled.zip",
            background=None  # Keep file until response is sent
        )
        
    except Exception as e:
        cleanup_temp_files(session_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-context")
async def generate_context(
    data_zip: UploadFile = File(...),
    names_json: UploadFile = File(...)
):
    """
    Endpoint 2: Generate context with people names
    
    Input:
    - data_zip: ZIP with 'memories' folder (original data)
    - names_json: JSON mapping person_X to names
    
    Output: ZIP with:
    - Named people folders (full, not sampled)
    - context.json in each memory folder
    
    Steps:
    1. Extract uploaded data
    2. Run face extraction (full)
    3. Apply names.json mapping
    4. Generate AI context with people identification
    5. Return complete annotated data
    """
    # Import heavy dependencies only when this endpoint is called
    try:
        from memory_to_people import MemoryPeopleExtractor
        from edit_pictures_based_on_json import PeopleFolderEditor
        from text_context_per_memory import MemoryContextAnalyzer
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Context generation not available. This endpoint requires opencv, face_recognition, and other heavy libraries."
        )
    
    session_id = f"session_{os.urandom(8).hex()}"
    session_dir = WORK_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"📦 Processing session: {session_id}")
        
        # Step 1: Extract data ZIP
        data_zip_path = session_dir / "data.zip"
        with open(data_zip_path, "wb") as f:
            content = await data_zip.read()
            f.write(content)
        
        print("📂 Extracting uploaded data...")
        extract_dir = session_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(data_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find memories folder
        memories_path = extract_dir / "memories"
        if not memories_path.exists():
            for item in extract_dir.rglob("memories"):
                if item.is_dir():
                    memories_path = item
                    break
        
        if not memories_path.exists():
            raise HTTPException(
                status_code=400,
                detail="No 'memories' folder found in uploaded ZIP"
            )
        
        # Step 2: Save names.json
        names_json_content = await names_json.read()
        names_mapping = json.loads(names_json_content)
        
        people_output = session_dir / "people"
        people_output.mkdir(exist_ok=True)
        
        names_json_path = people_output / "names.json"
        with open(names_json_path, 'w') as f:
            json.dump(names_mapping, f, indent=2)
        
        print("📝 names.json received")
        
        # Step 3: Extract faces (full, not sampled)
        print("🔍 Extracting faces...")
        extractor = MemoryPeopleExtractor(str(memories_path), str(people_output))
        extractor.process_all_memories()
        
        # Step 4: Convert names
        print("✏️  Converting person_X to actual names...")
        editor = PeopleFolderEditor(str(people_output), str(names_json_path))
        editor.process_names_mapping()
        
        # Step 5: Generate context with AI
        print("🤖 Generating context with AI...")
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not configured on server"
            )
        
        analyzer = MemoryContextAnalyzer(api_key, str(people_output))
        analyzer.process_all_memories(str(memories_path))
        
        # Step 6: Create output ZIP with everything
        print("📦 Creating complete output ZIP...")
        output_zip_path = session_dir / "complete_output.zip"
        
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all memories with context
            for memory_folder in memories_path.iterdir():
                if memory_folder.is_dir():
                    for file in memory_folder.rglob("*"):
                        if file.is_file():
                            arcname = f"memories/{memory_folder.name}/{file.relative_to(memory_folder)}"
                            zipf.write(file, arcname=arcname)
            
            # Add all people folders (full, named)
            for person_folder in people_output.iterdir():
                if person_folder.is_dir():
                    for file in person_folder.rglob("*"):
                        if file.is_file():
                            arcname = f"people/{person_folder.name}/{file.relative_to(person_folder)}"
                            zipf.write(file, arcname=arcname)
        
        print(f"✅ Session {session_id} complete")
        
        # Return complete ZIP
        return FileResponse(
            path=str(output_zip_path),
            media_type="application/zip",
            filename="complete_output.zip",
            background=None
        )
        
    except Exception as e:
        cleanup_temp_files(session_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup/{session_id}")
async def cleanup_session(session_id: str):
    """Clean up temporary files for a specific session"""
    try:
        cleanup_temp_files(session_id)
        return {"status": "cleaned", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TEXT-TO-SPEECH ENDPOINT
# ============================================================================

class TextToSpeechRequest(BaseModel):
    text: str
    name: str

def get_elevenlabs_voices() -> dict:
    """Get all voices from ElevenLabs and create name mapping"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        return {}
    
    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": api_key}
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {}
        
        voices = response.json().get("voices", [])
        
        # Create mapping: person_name -> voice_id
        # Looking for voices ending with "_voice_forgetmenot"
        voice_mapping = {}
        for voice in voices:
            voice_name = voice.get("name", "")
            voice_id = voice.get("voice_id", "")
            
            if voice_name.endswith("_voice_forgetmenot"):
                # Extract person name (e.g., "Tyler_voice_forgetmenot" -> "Tyler")
                person_name = voice_name.replace("_voice_forgetmenot", "")
                voice_mapping[person_name.lower()] = voice_id
        
        return voice_mapping
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return {}

def generate_speech_elevenlabs(text: str, voice_id: str) -> bytes:
    """Generate speech using ElevenLabs API"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not configured")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ElevenLabs API error: {response.text}"
            )
        
        return response.content
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

@app.post("/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """
    Generate speech from text using a person's voice clone
    
    Request body:
    {
        "text": "Hi, how are you?",
        "name": "Hannah"
    }
    
    Returns: MP3 audio file
    """
    
    # Get voice mapping
    voice_mapping = get_elevenlabs_voices()
    
    if not voice_mapping:
        raise HTTPException(
            status_code=500,
            detail="Could not load ElevenLabs voices. Check ELEVENLABS_API_KEY."
        )
    
    # Look up voice ID for this person
    person_name_lower = request.name.lower()
    voice_id = voice_mapping.get(person_name_lower)
    
    if not voice_id:
        available_names = ", ".join(voice_mapping.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Voice not found for '{request.name}'. Available: {available_names}"
        )
    
    # Generate speech
    try:
        audio_content = generate_speech_elevenlabs(request.text, voice_id)
        
        # Return as streaming MP3
        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename={request.name}_speech.mp3"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def list_voices():
    """List all available voice clones"""
    voice_mapping = get_elevenlabs_voices()
    
    if not voice_mapping:
        raise HTTPException(
            status_code=500,
            detail="Could not load voices. Check ELEVENLABS_API_KEY."
        )
    
    return {
        "voices": list(voice_mapping.keys()),
        "count": len(voice_mapping)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
