# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ReMind** is a multimodal AI platform designed to help Alzheimer's patients reconnect with their memories through intelligent, emotionally aware "memory replays." It combines retrieval, generation, and empathetic interaction — enabling patients to revisit key life moments while caregivers monitor emotional and cognitive progress.

## Architecture

The system consists of three main components:

### 1. **Data Pipeline (scripts/)**
- **GCS → Metadata → Snowflake**: Extracts context from Google Cloud Storage, generates metadata CSV, uploads to Snowflake with vector embeddings
- **Key Scripts**:
  - `build_metadata_from_context.py`: Queries GCS bucket for `context.json` files and generates `data/metadata.csv`
  - `upload_to_snowflake.py`: Uploads metadata to Snowflake MEMORY_VAULT with embeddings using `CORTEX.EMBED_TEXT_768()`
  - `search_memories.py`: Basic semantic search using Snowflake Cortex vector similarity
  - `retrieval_cycle.py`: **Complete retrieval cycle** - Query → Search → Gemini Summarization
    - Converts user questions to vector embeddings
    - Retrieves top-K semantically similar memories
    - Uses Gemini to synthesize natural language answers
    - Falls back to rule-based summaries if Gemini unavailable

### 2. **Processing Pipeline (processing_script/)**
- **Face extraction and naming**: Uses face-recognition library to extract and name people from videos/images
- **Context generation**: Uses Gemini to generate descriptions and context for memory clips
- **Voice extraction**: Extracts audio from videos and uploads to ElevenLabs for voice cloning
- **Sequential pipeline**: Run `RUN_ALL_PIPELINE.py` to execute the complete processing workflow

### 3. **API Server (api_server/)**
- **FastAPI-based REST API**: Provides endpoints for transcription, text-to-speech, and lip-sync video generation
- **Main application**: `main.py` (root) serves as entry point
- **Endpoints**:
  - Transcription: Speech-to-text using Gemini/WhisperX
  - Text-to-Speech: ElevenLabs voice synthesis
  - Lip-sync: Gooey.AI integration for video generation with synchronized audio

### 4. **Snowflake Memory Vault**
- **Central database**: Stores all memory clips with multimodal embeddings
- **Schema** (`MEMORY_VAULT` table):
  ```sql
  - id: UUID
  - event_name: Event/trip name (e.g., "ski trip", "disney trip")
  - file_name: Original filename
  - file_type: "video" or "image"
  - description: AI-generated context description
  - people: ARRAY of people names in the memory
  - event_summary: High-level event description
  - file_url: GCS public URL
  - embedding: VECTOR(FLOAT, 768) - semantic embedding for search
  ```
- **Vector Search**: Uses `VECTOR_COSINE_SIMILARITY()` with Snowflake Cortex embeddings for semantic retrieval

## Commands

### Data Pipeline (scripts/)

```bash
cd scripts

# Generate metadata from GCS context.json files
python build_metadata_from_context.py

# Upload metadata to Snowflake with embeddings
python upload_to_snowflake.py

# Interactive semantic search (basic vector similarity)
python search_memories.py
python search_memories.py --query "disney trip with Anna" --top-k 5

# Retrieval Cycle (search + Gemini summarization)
python retrieval_cycle.py                                    # Interactive mode
python retrieval_cycle.py --query "What did we eat at Disney?" --top-k 5
python retrieval_cycle.py --test                             # Test queries
```

### Processing Pipeline (processing_script/)

```bash
cd processing_script

# Complete pipeline (extracts faces, names people, generates context, uploads voices)
python RUN_ALL_PIPELINE.py

# Individual steps
python 1_extract_faces.py          # Extract faces from videos/images
python 2_convert_names.py          # Name people using face recognition
python 3_generate_context.py       # Generate context using Gemini
python 4_extract_and_upload_voices.py  # Upload voices to ElevenLabs
```

### API Server (api_server/)

```bash
cd api_server

# Start production server
./start_server.sh

# Start test server (development mode)
./start_test_server.sh

# Direct uvicorn command
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Main Application (root)

```bash
# Start main FastAPI app
uvicorn main:app --reload
```

## Environment Setup

Create a `.env` file in the project root with:

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

# ElevenLabs (for voice synthesis)
ELEVENLABS_API_KEY=your_key

# Gemini API
GEMINI_API_KEY=your_key
```

## Key Technical Details

### Unicode Handling in Metadata Generation
The `build_metadata_from_context.py` script handles a special case: GCS filenames use regular spaces, but `context.json` keys use Unicode non-breaking spaces (U+202F) before AM/PM in timestamps. The `normalize_key()` function converts filenames like `"Screenshot 2025-10-04 at 3.37.37 PM.png"` to match keys like `"Screenshot 2025-10-04 at 3.37.37\u202fPM_context"`.

### Embedding Generation
- **Initially attempted**: Snowflake Cortex REST API (failed with empty array errors)
- **Current approach**: Use Snowflake's native `SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', text)` function directly in SQL INSERT statements
- **Model**: e5-base-v2 (768 dimensions)
- **Storage**: VECTOR(FLOAT, 768) type in Snowflake

### Data Flow
1. Videos/images uploaded to GCS bucket organized by event folders
2. Processing pipeline generates `context.json` with AI descriptions and people names
3. `build_metadata_from_context.py` reads context files → CSV
4. `upload_to_snowflake.py` inserts to MEMORY_VAULT with embeddings
5. **Retrieval Cycle**:
   - User asks: "What did we eat at Disney?"
   - `retrieval_cycle.py` converts query → embedding
   - Snowflake finds top-K similar memories using `VECTOR_COSINE_SIMILARITY()`
   - Gemini synthesizes natural answer from retrieved contexts
   - Returns: "Looking at your disney trip memories, I can see a Mickey Mouse cinnamon roll..."
6. API endpoints (future) integrate retrieval cycle for voice/video responses

### Retrieval Cycle Architecture

```
User Query: "What did we eat at Disney?"
         ↓
1. CORTEX.EMBED_TEXT_768(query) → [768-dim vector]
         ↓
2. SELECT * FROM MEMORY_VAULT
   ORDER BY VECTOR_COSINE_SIMILARITY(embedding, query_vector)
   LIMIT 5
         ↓
3. Retrieved Memories → Gemini Prompt
         ↓
4. Gemini generates: "Looking at your disney trip memories,
   I can see: A Mickey Mouse shaped cinnamon roll with
   diced apples and chocolate chips..."
         ↓
5. Return answer + source memories
```

### SnowflakeClient Pattern
The `lib/snowflake_client.py` provides a context manager for database operations:
```python
with SnowflakeClient() as client:
    results = search_memories(query, client)
```

## Tech Stack

- **Database + Retrieval**: Snowflake Cortex (CORTEX.EMBED_TEXT, VECTOR_COSINE_SIMILARITY)
- **Storage**: Google Cloud Storage (GCS)
- **AI Models**:
  - Gemini 1.5 Pro (context generation, intent parsing)
  - e5-base-v2 (text embeddings via Snowflake Cortex)
  - ElevenLabs (voice synthesis)
  - Veo (video generation - planned)
  - WhisperX (speech-to-text - planned)
- **Backend**: Python, FastAPI
- **Key Libraries**:
  - `snowflake-connector-python`: Database connection
  - `google-cloud-storage`: GCS integration
  - `google-generativeai`: Gemini API
  - `face-recognition`: Face extraction and matching
  - `pandas`: Data processing

## Project Structure Notes

- **scripts/**: Production data pipeline for GCS → Snowflake
- **processing_script/**: One-time processing to generate context from raw videos
- **api_server/**: REST API for memory interaction (transcription, TTS, lip-sync)
- **api/**: Additional API routers (included in main.py)
- **lib/**: Shared utilities (config, Snowflake client)
- **data/**: Generated metadata CSV files
- **models/**: (Future) ML model files
- **services/**: (Future) Business logic layer

## Future Expansion

- Multi-user family memory linking
- Emotion tracking over time via LLM summaries
- Caregiver alert system for confusion/distress detection
- Interactive chat with memories using Gemini
- Video generation with Veo for "living memories"
