# ForgetMeNot API Server

FastAPI server for processing memories: face extraction, name mapping, and AI context generation.

---

## 🚀 **Quick Start**

### **1. Install Dependencies**

```bash
cd api_server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Configure Environment**

Create `.env` file:

```bash
GEMINI_API_KEY=your_api_key_here
```

### **3. Run Server**

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Server will start at: `http://localhost:8000`

---

## 📡 **API Endpoints**

### **Endpoint 1: Extract Faces (Sample)**

```
POST /extract-faces
```

**Purpose:** Extract faces from memories and return 16 random samples per person for review.

**Input:**
- `data_zip`: ZIP file containing `memories/` folder with videos/images

**Output:**
- ZIP file with `people/person_1/`, `people/person_2/`, etc.
- Each folder has 16 randomly sampled face images
- Includes `metadata.json` for each person

**Example with cURL:**

```bash
curl -X POST "http://localhost:8000/extract-faces" \
  -H "accept: application/json" \
  -F "data_zip=@memories.zip" \
  --output people_sampled.zip
```

**Example with Python:**

```python
import requests

with open("memories.zip", "rb") as f:
    files = {"data_zip": f}
    response = requests.post("http://localhost:8000/extract-faces", files=files)
    
with open("people_sampled.zip", "wb") as f:
    f.write(response.content)
```

---

### **Endpoint 2: Generate Context (Full)**

```
POST /generate-context
```

**Purpose:** Complete pipeline - face extraction, name mapping, and AI context generation.

**Input:**
- `data_zip`: ZIP file containing `memories/` folder
- `names_json`: names.json file mapping person_X to actual names

**Output:**
- ZIP file with complete annotated data:
  - `memories/` - All videos/images with `context.json` in each folder
  - `people/` - Named folders (anna/, lisa/, etc.) with ALL face images

**Example with cURL:**

```bash
curl -X POST "http://localhost:8000/generate-context" \
  -H "accept: application/json" \
  -F "data_zip=@memories.zip" \
  -F "names_json=@names.json" \
  --output complete_output.zip
```

**Example with Python:**

```python
import requests

files = {
    "data_zip": open("memories.zip", "rb"),
    "names_json": open("names.json", "rb")
}

response = requests.post("http://localhost:8000/generate-context", files=files)

with open("complete_output.zip", "wb") as f:
    f.write(response.content)
```

---

### **Endpoint 3: Health Check**

```
GET /
```

Check if server is running.

**Response:**
```json
{
  "status": "online",
  "service": "ForgetMeNot API",
  "version": "1.0.0"
}
```

---

### **Endpoint 4: Cleanup**

```
DELETE /cleanup/{session_id}
```

Clean up temporary files for a specific session.

---

## 📁 **File Formats**

### **Input: memories.zip**

```
memories.zip
└── memories/
    ├── day in college/
    │   ├── video1.mp4
    │   ├── video2.mp4
    │   └── image1.jpg
    └── ski trip/
        └── video.mp4
```

### **Input: names.json**

```json
{
  "anna": "person_1",
  "lisa": "person_2,person_7",
  "bob": "person_4"
}
```

or

```json
{
  "person_1": "anna",
  "person_2": "lisa",
  "person_4": "bob"
}
```

### **Output: people_sampled.zip** (from `/extract-faces`)

```
people_sampled.zip
└── people/
    ├── person_1/
    │   ├── face_0000.jpg
    │   ├── face_0001.jpg
    │   ├── ... (16 samples)
    │   └── metadata.json
    ├── person_2/
    └── person_3/
```

### **Output: complete_output.zip** (from `/generate-context`)

```
complete_output.zip
├── memories/
│   ├── day in college/
│   │   ├── video1.mp4
│   │   ├── video2.mp4
│   │   └── context.json          ← AI-generated
│   └── ski trip/
│       └── context.json
└── people/
    ├── anna/                       ← Named folders
    │   ├── face_0000.jpg
    │   ├── ... (ALL faces)
    │   └── metadata.json
    ├── lisa/
    └── bob/
```

**context.json format:**

```json
{
  "memory_context": "Overall memory description",
  "video1_context": "Anna and Lisa shopping at Target...",
  "video1_people": "anna, lisa",
  "video2_context": "Bob playing basketball...",
  "video2_people": "bob"
}
```

---

## 🔧 **Workflow**

### **Two-Step Workflow (Recommended)**

**Step 1:** Extract faces and review

```bash
# Upload memories, get sampled faces
curl -X POST "http://localhost:8000/extract-faces" \
  -F "data_zip=@memories.zip" \
  --output people_sampled.zip

# Unzip and review person_1/, person_2/, etc.
unzip people_sampled.zip

# Create names.json mapping
nano names.json
```

**Step 2:** Generate full context

```bash
# Upload memories + names.json, get complete output
curl -X POST "http://localhost:8000/generate-context" \
  -F "data_zip=@memories.zip" \
  -F "names_json=@names.json" \
  --output complete_output.zip
```

---

## 🌐 **Interactive API Docs**

Once server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Try the endpoints directly in the browser!

---

## ⚙️ **Configuration**

### **Environment Variables**

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes (for `/generate-context`) | Google Gemini API key |

### **Server Settings**

Edit `main.py` or use command line:

```bash
# Change port
uvicorn main:app --port 3000

# Enable auto-reload for development
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📊 **Processing Details**

### **Face Extraction**
- Uses `face_recognition` library (HOG model)
- Clusters faces with DBSCAN (tolerance=0.3, strict)
- Extracts faces from videos at 1 FPS

### **Context Generation**
- Uses Google Gemini 2.0 Flash
- Loads 3 reference images per person
- Analyzes videos with both visual and audio
- Identifies people in scenes using face references

---

## 🔒 **Security Notes**

- Server stores temporary files in `temp_processing/`
- Each session gets unique ID
- Files are NOT auto-deleted (call `/cleanup/{session_id}` or delete manually)
- Don't expose to public internet without authentication!

---

## 🐛 **Troubleshooting**

**"GEMINI_API_KEY not configured"**
- Create `.env` file in `api_server/` directory
- Add `GEMINI_API_KEY=your_key`

**"No 'memories' folder found"**
- ZIP must contain a `memories/` folder at root
- Or nested like `data/memories/`

**Large file uploads fail**
- Increase uvicorn timeout: `--timeout-keep-alive 300`
- Increase max request size in nginx/reverse proxy

**Processing takes too long**
- Use `/extract-faces` first to verify data
- `/generate-context` can take 1-5 min per video

---

## 📝 **Example Client Script**

```python
import requests
import zipfile
import json
from pathlib import Path

API_URL = "http://localhost:8000"

def process_memories(memories_zip_path, names_mapping):
    """Complete workflow: extract faces, map names, generate context"""
    
    # Step 1: Extract faces (sampled)
    print("Step 1: Extracting faces...")
    with open(memories_zip_path, "rb") as f:
        response = requests.post(
            f"{API_URL}/extract-faces",
            files={"data_zip": f}
        )
    
    # Save sampled faces
    with open("people_sampled.zip", "wb") as f:
        f.write(response.content)
    
    print("✅ Faces extracted. Review people_sampled.zip")
    
    # Step 2: User creates names.json (manual step)
    input("Edit names.json and press Enter to continue...")
    
    # Step 3: Generate context
    print("Step 2: Generating context...")
    files = {
        "data_zip": open(memories_zip_path, "rb"),
        "names_json": ("names.json", json.dumps(names_mapping), "application/json")
    }
    
    response = requests.post(
        f"{API_URL}/generate-context",
        files=files
    )
    
    # Save complete output
    with open("complete_output.zip", "wb") as f:
        f.write(response.content)
    
    print("✅ Complete! Check complete_output.zip")

# Example usage
names = {
    "anna": "person_1",
    "lisa": "person_2",
    "bob": "person_4"
}

process_memories("memories.zip", names)
```

---

## 📚 **Additional Resources**

- Original processing scripts: `../processing_script/`
- FastAPI docs: https://fastapi.tiangolo.com/
- Face recognition: https://github.com/ageitgey/face_recognition
