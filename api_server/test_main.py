"""
Test version of FastAPI server for ForgetMeNot
Returns mock data and validates inputs without doing actual processing
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import zipfile
import json
import io
from pathlib import Path
from PIL import Image

app = FastAPI(title="ForgetMeNot API (Test Mode)", version="1.0.0-test")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_zip_structure(zip_content: bytes) -> dict:
    """Validate that uploaded ZIP has correct structure"""
    try:
        zip_buffer = io.BytesIO(zip_content)
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            # Check for memories folder
            has_memories = any('memories/' in f for f in file_list)
            
            # Count video/image files
            video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
            
            videos = [f for f in file_list if Path(f).suffix.lower() in video_extensions]
            images = [f for f in file_list if Path(f).suffix.lower() in image_extensions]
            
            # Get memory folders
            memory_folders = set()
            for f in file_list:
                if 'memories/' in f:
                    parts = f.split('memories/')[1].split('/')[0]
                    if parts:
                        memory_folders.add(parts)
            
            return {
                "valid": has_memories,
                "has_memories_folder": has_memories,
                "memory_count": len(memory_folders),
                "memory_folders": sorted(list(memory_folders)),
                "video_count": len(videos),
                "image_count": len(images),
                "total_files": len(file_list),
                "sample_files": file_list[:10]
            }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

def validate_names_json(json_content: bytes) -> dict:
    """Validate names.json format"""
    try:
        names_mapping = json.loads(json_content)
        
        if not isinstance(names_mapping, dict):
            return {
                "valid": False,
                "error": "names.json must be a JSON object/dict"
            }
        
        # Detect format
        first_key = list(names_mapping.keys())[0] if names_mapping else ""
        format_type = "person_to_name" if first_key.startswith('person_') else "name_to_person"
        
        # Count mappings
        person_count = len(names_mapping)
        
        # Check for merges (comma-separated values)
        merge_count = sum(1 for v in names_mapping.values() if isinstance(v, str) and ',' in v)
        
        # Check for deletions (null values)
        delete_count = sum(1 for v in names_mapping.values() if v is None or v == "")
        
        return {
            "valid": True,
            "format": format_type,
            "person_count": person_count,
            "merge_count": merge_count,
            "delete_count": delete_count,
            "sample_mapping": dict(list(names_mapping.items())[:5])
        }
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": f"Invalid JSON: {str(e)}"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

def create_mock_people_zip() -> io.BytesIO:
    """Create a mock people_sampled.zip with test data"""
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Create mock person folders
        for person_id in range(1, 4):  # person_1, person_2, person_3
            person_name = f"person_{person_id}"
            
            # Add 16 mock face images
            for face_id in range(16):
                # Create a small test image
                img = Image.new('RGB', (100, 100), color=(73 * person_id, 109, 137))
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG')
                img_buffer.seek(0)
                
                arcname = f"people/{person_name}/face_{face_id:04d}.jpg"
                zipf.writestr(arcname, img_buffer.getvalue())
            
            # Add mock metadata
            metadata = {
                "person_id": person_id,
                "total_appearances": 50 + person_id * 20,
                "sources": [
                    {"memory": "test_memory_1", "count": 20},
                    {"memory": "test_memory_2", "count": 15}
                ]
            }
            zipf.writestr(
                f"people/{person_name}/metadata.json",
                json.dumps(metadata, indent=2)
            )
    
    buffer.seek(0)
    return buffer

def create_mock_complete_zip() -> io.BytesIO:
    """Create a mock complete_output.zip with test data"""
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add mock memories with context
        memories = ["day_in_college", "ski_trip"]
        
        for memory in memories:
            # Add mock context.json
            context = {
                "memory_context": f"{memory} - A memorable day with friends",
                "video1_context": "Anna and Lisa exploring the campus on a sunny afternoon.",
                "video1_people": "anna, lisa",
                "video2_context": "Bob preparing breakfast in the kitchen.",
                "video2_people": "bob"
            }
            zipf.writestr(
                f"memories/{memory}/context.json",
                json.dumps(context, indent=2)
            )
            
            # Add mock video placeholder
            zipf.writestr(
                f"memories/{memory}/video1.txt",
                "Mock video file - would be .mp4 in real output"
            )
        
        # Add mock named people folders
        people_names = ["anna", "lisa", "bob"]
        
        for name in people_names:
            # Add mock face images
            for face_id in range(5):  # Just 5 for the mock
                img = Image.new('RGB', (100, 100), color=(100, 150, 200))
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG')
                img_buffer.seek(0)
                
                arcname = f"people/{name}/face_{face_id:04d}.jpg"
                zipf.writestr(arcname, img_buffer.getvalue())
            
            # Add metadata
            metadata = {
                "name": name,
                "total_appearances": 50,
                "sources": [{"memory": "test_memory", "count": 50}]
            }
            zipf.writestr(
                f"people/{name}/metadata.json",
                json.dumps(metadata, indent=2)
            )
    
    buffer.seek(0)
    return buffer

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "ForgetMeNot API (TEST MODE)",
        "version": "1.0.0-test",
        "mode": "test",
        "note": "This is a test server. It validates inputs and returns mock data."
    }

@app.post("/extract-faces")
async def extract_faces(data_zip: UploadFile = File(...)):
    """
    TEST MODE: Validate input and return mock people data
    
    This endpoint:
    1. Validates the uploaded ZIP structure
    2. Returns mock person_1, person_2, person_3 folders
    3. Does NOT actually extract faces
    """
    
    # Read uploaded file
    content = await data_zip.read()
    
    # Validate ZIP structure
    validation = validate_zip_structure(content)
    
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid ZIP structure",
                "validation": validation
            }
        )
    
    # Check if memories folder exists
    if not validation["has_memories_folder"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "No 'memories' folder found in ZIP",
                "validation": validation
            }
        )
    
    # Return validation info + mock data
    print("✅ Validation passed:")
    print(f"  - Memories found: {validation['memory_count']} folders")
    print(f"  - Videos: {validation['video_count']}")
    print(f"  - Images: {validation['image_count']}")
    print("📦 Returning mock people data (3 person folders)")
    
    # Create mock ZIP
    mock_zip = create_mock_people_zip()
    
    return StreamingResponse(
        mock_zip,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=people_sampled_MOCK.zip",
            "X-Test-Mode": "true",
            "X-Validation": json.dumps(validation)
        }
    )

@app.post("/generate-context")
async def generate_context(
    data_zip: UploadFile = File(...),
    names_json: UploadFile = File(...)
):
    """
    TEST MODE: Validate inputs and return mock complete data
    
    This endpoint:
    1. Validates the uploaded ZIP structure
    2. Validates names.json format
    3. Returns mock complete output with context
    4. Does NOT actually process faces or generate AI context
    """
    
    # Read uploaded files
    data_content = await data_zip.read()
    names_content = await names_json.read()
    
    # Validate data ZIP
    data_validation = validate_zip_structure(data_content)
    
    if not data_validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid data ZIP structure",
                "validation": data_validation
            }
        )
    
    if not data_validation["has_memories_folder"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "No 'memories' folder found in ZIP",
                "validation": data_validation
            }
        )
    
    # Validate names.json
    names_validation = validate_names_json(names_content)
    
    if not names_validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid names.json format",
                "validation": names_validation
            }
        )
    
    # Return validation info + mock data
    print("✅ Data ZIP validation passed:")
    print(f"  - Memories: {data_validation['memory_count']} folders")
    print(f"  - Videos: {data_validation['video_count']}")
    print(f"  - Images: {data_validation['image_count']}")
    print()
    print("✅ names.json validation passed:")
    print(f"  - Format: {names_validation['format']}")
    print(f"  - People: {names_validation['person_count']}")
    print(f"  - Merges: {names_validation['merge_count']}")
    print(f"  - Deletes: {names_validation['delete_count']}")
    print()
    print("📦 Returning mock complete output with context")
    
    # Create mock complete ZIP
    mock_zip = create_mock_complete_zip()
    
    return StreamingResponse(
        mock_zip,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=complete_output_MOCK.zip",
            "X-Test-Mode": "true",
            "X-Data-Validation": json.dumps(data_validation),
            "X-Names-Validation": json.dumps(names_validation)
        }
    )

@app.post("/validate-data")
async def validate_data(data_zip: UploadFile = File(...)):
    """
    Validate data ZIP structure without processing
    Returns detailed validation info
    """
    content = await data_zip.read()
    validation = validate_zip_structure(content)
    
    return {
        "validation": validation,
        "recommendations": {
            "valid": validation["valid"],
            "ready_to_process": validation.get("has_memories_folder", False),
            "warnings": []
        }
    }

@app.post("/validate-names")
async def validate_names(names_json: UploadFile = File(...)):
    """
    Validate names.json format without processing
    Returns detailed validation info
    """
    content = await names_json.read()
    validation = validate_names_json(content)
    
    return {
        "validation": validation,
        "recommendations": {
            "valid": validation["valid"],
            "format_detected": validation.get("format", "unknown")
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("="*70)
    print("Starting ForgetMeNot API in TEST MODE")
    print("="*70)
    print()
    print("This server validates inputs and returns mock data.")
    print("No actual face extraction or AI processing will occur.")
    print()
    print("API Docs: http://localhost:8001/docs")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8001)
