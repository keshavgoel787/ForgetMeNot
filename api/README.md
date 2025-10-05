# ReMind API Documentation

Complete FastAPI implementation for ReMind's memory retrieval and data pipeline operations.

## Overview

This API provides comprehensive endpoints for:
- **Memory Search & Retrieval**: AI-powered semantic search with natural language queries
- **Metadata Management**: Build metadata from GCS context files
- **Data Upload**: Upload files to GCS and metadata to Snowflake
- **Transcription**: Audio transcription and analysis

## Quick Start

### Start the Server

```bash
# From project root
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# The API will be available at:
# - API: http://localhost:8000
# - Interactive Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Test the API

```bash
# Health check
curl http://localhost:8000/

# Search memories
curl -X POST "http://localhost:8000/memories/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What did we eat at Disney?", "top_k": 5}'
```

## API Endpoints

### 🧠 Memory Search & Retrieval (`/memories`)

#### POST `/memories/search`
Search memories and generate AI-powered answers.

**Request:**
```json
{
  "query": "What did we eat at Disney?",
  "top_k": 5,
  "show_sources": true
}
```

**Response:**
```json
{
  "status": "success",
  "answer": "Looking at your disney trip memories with Anna, I can see a Mickey Mouse shaped cinnamon roll with diced apples and chocolate chips...",
  "memories": [
    {
      "event_name": "disney trip",
      "file_name": "IMG_1234.jpg",
      "file_type": "image",
      "description": "A Mickey Mouse shaped cinnamon roll...",
      "people": ["Anna"],
      "event_summary": "Family trip to Disneyland",
      "file_url": "https://storage.googleapis.com/...",
      "similarity": 0.89
    }
  ],
  "query": "What did we eat at Disney?",
  "model_used": "gemini-2.5-flash"
}
```

#### GET `/memories/search`
Alternative GET endpoint for simple queries.

```bash
curl "http://localhost:8000/memories/search?query=What%20did%20we%20eat%20at%20Disney?&top_k=5"
```

#### GET `/memories/health`
Check Snowflake connection and memory count.

**Response:**
```json
{
  "status": "healthy",
  "snowflake_connected": true,
  "total_memories": 142
}
```

---

### 📊 Metadata Management (`/metadata`)

#### POST `/metadata/build`
Build metadata CSV from GCS context.json files.

**Response:**
```json
{
  "status": "success",
  "rows_generated": 142,
  "metadata": [...],
  "csv_path": "/path/to/data/metadata.csv",
  "message": "Successfully generated 142 metadata rows from GCS"
}
```

**What it does:**
1. Scans all event folders in GCS bucket
2. Reads `context.json` from each folder
3. Extracts file metadata, descriptions, and people
4. Saves to `data/metadata.csv`

#### GET `/metadata/count`
Get count of metadata rows in existing CSV.

**Response:**
```json
{
  "status": "success",
  "count": 142,
  "csv_path": "/path/to/data/metadata.csv"
}
```

---

### ⬆️ Upload Operations (`/upload`)

#### POST `/upload/snowflake`
Upload metadata CSV to Snowflake MEMORY_VAULT.

**Request:**
```json
{
  "csv_path": "data/metadata.csv",
  "truncate_existing": true
}
```

**Response:**
```json
{
  "status": "success",
  "records_uploaded": 140,
  "records_skipped": 2,
  "total_records": 142,
  "message": "Successfully uploaded 140/142 records to Snowflake"
}
```

**What it does:**
1. Reads metadata CSV
2. Optionally truncates existing MEMORY_VAULT data
3. Inserts records with embeddings using `CORTEX.EMBED_TEXT_768`
4. Returns upload statistics

#### POST `/upload/gcs`
Upload video or image file to Google Cloud Storage.

**Request (multipart/form-data):**
- `file`: Video/image file
- `event_name`: Event folder name (default: "general")

**Response:**
```json
{
  "status": "success",
  "file_url": "https://storage.googleapis.com/forgetmenot-videos/disney%20trip/video.mp4",
  "bucket": "forgetmenot-videos",
  "blob_name": "disney trip/video.mp4",
  "event_name": "disney trip",
  "file_type": "video",
  "message": "Successfully uploaded video.mp4 to disney trip/"
}
```

**Supported formats:**
- Videos: mp4, mov, avi, mkv
- Images: jpg, jpeg, png, gif, webp

---

### 🎤 Transcription (`/transcribe`)

#### POST `/transcribe/`
Transcribe audio file and analyze with Gemini.

**Request (multipart/form-data):**
- `file`: Audio file (WAV, MP3, FLAC, etc.)

**Response:**
```json
{
  "status": "success",
  "transcript": "I remember going to Disney with Anna...",
  "context": {
    "people": ["Anna"],
    "location": "Disneyland",
    "emotions": ["happy", "excited"]
  }
}
```

---

## Complete Data Pipeline Workflow

### Option 1: Manual Step-by-Step

```bash
# 1. Build metadata from GCS
curl -X POST http://localhost:8000/metadata/build

# 2. Upload to Snowflake
curl -X POST http://localhost:8000/upload/snowflake \
  -H "Content-Type: application/json" \
  -d '{"csv_path": "data/metadata.csv", "truncate_existing": true}'

# 3. Search memories
curl -X POST http://localhost:8000/memories/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What did we eat at Disney?", "top_k": 5}'
```

### Option 2: Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Build metadata
response = requests.post(f"{BASE_URL}/metadata/build")
print(f"Built {response.json()['rows_generated']} metadata rows")

# Upload to Snowflake
response = requests.post(f"{BASE_URL}/upload/snowflake", json={
    "csv_path": "data/metadata.csv",
    "truncate_existing": True
})
print(f"Uploaded {response.json()['records_uploaded']} records")

# Search memories
response = requests.post(f"{BASE_URL}/memories/search", json={
    "query": "What did we eat at Disney?",
    "top_k": 5
})
result = response.json()
print(f"Answer: {result['answer']}")
print(f"Found {len(result['memories'])} source memories")
```

### Option 3: Upload New File and Process

```python
import requests

BASE_URL = "http://localhost:8000"

# Upload file to GCS
with open("my_video.mp4", "rb") as f:
    files = {"file": f}
    data = {"event_name": "disney trip"}
    response = requests.post(f"{BASE_URL}/upload/gcs", files=files, data=data)
    print(f"Uploaded: {response.json()['file_url']}")

# After processing pipeline generates context.json...
# Rebuild metadata
requests.post(f"{BASE_URL}/metadata/build")

# Re-upload to Snowflake
requests.post(f"{BASE_URL}/upload/snowflake", json={"truncate_existing": True})

# Search
response = requests.post(f"{BASE_URL}/memories/search", json={
    "query": "Tell me about the disney trip"
})
print(response.json()["answer"])
```

---

## Environment Variables

Ensure these are set in your `.env` file:

```bash
# Snowflake
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=MEMORY_DB
SNOWFLAKE_SCHEMA=PUBLIC

# Google Cloud
GCS_BUCKET=forgetmenot-videos
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Gemini API
GEMINI_API_KEY=your_gemini_key

# ElevenLabs (optional)
ELEVENLABS_API_KEY=your_key
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ReMind FastAPI Server                     │
│                     (main.py - Port 8000)                    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌──────────────────┐   ┌──────────────┐
│  /memories    │   │   /metadata      │   │   /upload    │
│               │   │                  │   │              │
│ - search      │   │ - build          │   │ - snowflake  │
│ - health      │   │ - count          │   │ - gcs        │
└───────────────┘   └──────────────────┘   └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌──────────────────┐   ┌──────────────┐
│  Snowflake    │   │   Google Cloud   │   │  Snowflake   │
│  MEMORY_VAULT │◄──│   Storage (GCS)  │──►│  + GCS       │
│               │   │                  │   │              │
│ - Vector DB   │   │ - Raw files      │   │ - Ingest     │
│ - Cortex AI   │   │ - context.json   │   │ - Embeddings │
└───────────────┘   └──────────────────┘   └──────────────┘
        │
        ▼
┌───────────────┐
│  Gemini API   │
│               │
│ - Answer Gen  │
│ - Synthesis   │
└───────────────┘
```

---

## Error Handling

All endpoints return standard error responses:

```json
{
  "status": "error",
  "error": "Brief error message",
  "detail": "Detailed error information"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Resource not found (e.g., CSV doesn't exist)
- `500`: Internal server error (database/API failures)

---

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- View all endpoints
- Test API calls directly from the browser
- See request/response schemas
- Download OpenAPI specification

---

## Development

### Project Structure

```
ForgetMeNot/
├── main.py                    # FastAPI app entry point
├── api/
│   ├── __init__.py
│   ├── schemas.py             # Pydantic models
│   ├── memories.py            # Memory search routes
│   ├── metadata.py            # Metadata management routes
│   ├── upload.py              # Upload routes
│   └── transcribe.py          # Transcription routes
├── scripts/
│   ├── lib/
│   │   ├── config.py          # Configuration
│   │   └── snowflake_client.py # Snowflake client
│   ├── retrieval_cycle.py     # Core retrieval logic
│   ├── build_metadata_from_context.py
│   └── upload_to_snowflake.py
└── data/
    └── metadata.csv           # Generated metadata
```

### Adding New Endpoints

1. Create route in `api/` directory
2. Define Pydantic schemas in `api/schemas.py`
3. Import and include router in `main.py`
4. Update this README with endpoint documentation

---

## Production Deployment

```bash
# Install production dependencies
pip install uvicorn[standard] gunicorn

# Run with Gunicorn (production)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use the startup scripts
./start_server.sh      # Production mode
./start_test_server.sh # Development mode
```

---

## Support

For issues or questions:
- Check `/docs` endpoint for interactive API documentation
- Review error messages in responses
- Ensure all environment variables are set correctly
- Verify Snowflake and GCS connections using health endpoints
