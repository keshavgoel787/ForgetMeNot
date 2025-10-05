# ReMind API Deployment Guide

## 🚀 Deploy to Render (Recommended - Free)

### Step 1: Push to GitHub
```bash
git add requirements.txt render.yaml
git commit -m "Add deployment config"
git push origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo: `keshavgoel787/ForgetMeNot`
4. Render will auto-detect `render.yaml`
5. Click **"Apply"**

### Step 3: Add Environment Variables
In Render dashboard, add these:

```
SNOWFLAKE_USER=your_snowflake_user
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=MEMORY_DB
SNOWFLAKE_SCHEMA=PUBLIC
GCS_BUCKET=forgetmenot-videos
GEMINI_API_KEY=your_gemini_api_key
```

### Step 4: Get Your API URL
After deployment, Render gives you a URL like:
```
https://remind-api.onrender.com
```

**Give this URL to your teammate** - they'll use it in their HTML:
```javascript
fetch('https://remind-api.onrender.com/memories/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "Anna and I at the beach",
    top_k: 5,
    show_sources: true
  })
})
```

---

## Alternative: Deploy to Railway

### Step 1: Install Railway CLI
```bash
npm i -g @railway/cli
railway login
```

### Step 2: Deploy
```bash
cd /Users/keshavgoel/ForgetMeNot
railway init
railway up
```

### Step 3: Set Environment Variables
```bash
railway variables set SNOWFLAKE_USER=your_user
railway variables set SNOWFLAKE_PASSWORD=your_password
railway variables set SNOWFLAKE_ACCOUNT=your_account
railway variables set SNOWFLAKE_WAREHOUSE=COMPUTE_WH
railway variables set SNOWFLAKE_DATABASE=MEMORY_DB
railway variables set SNOWFLAKE_SCHEMA=PUBLIC
railway variables set GCS_BUCKET=forgetmenot-videos
railway variables set GEMINI_API_KEY=your_key
```

### Step 4: Get URL
```bash
railway open
# Your API will be at: https://your-app.railway.app
```

---

## API Endpoints for Your Teammate

### 1. Search Memories (Main Endpoint)
```
POST https://your-api-url.com/memories/search
```

**Request:**
```json
{
  "query": "Anna and I holding hands at the beach",
  "top_k": 5,
  "show_sources": true
}
```

**Response:**
```json
{
  "status": "success",
  "answer": "AI-generated narrative about the memory...",
  "memories": [
    {
      "file_url": "https://storage.googleapis.com/...",
      "file_type": "video",
      "description": "...",
      "people": ["Anna"],
      "similarity": 0.89
    }
  ],
  "query": "Anna and I holding hands at the beach"
}
```

### 2. Get Metadata Count
```
GET https://your-api-url.com/metadata/count
```

### 3. Health Check
```
GET https://your-api-url.com/memories/health
```

### 4. API Documentation
```
GET https://your-api-url.com/docs
```

---

## Example HTML Integration

Your teammate can use this code:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Memory Search</title>
</head>
<body>
    <h1>Therapist Memory Upload</h1>

    <textarea id="prompt" placeholder="Enter memory description..."></textarea>
    <button onclick="searchMemories()">Search</button>

    <div id="results"></div>

    <script>
        const API_URL = 'https://remind-api.onrender.com'; // Your deployed URL

        async function searchMemories() {
            const prompt = document.getElementById('prompt').value;

            const response = await fetch(`${API_URL}/memories/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: prompt,
                    top_k: 5,
                    show_sources: true
                })
            });

            const data = await response.json();

            // Display results
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <h2>AI Narrative:</h2>
                <p>${data.answer}</p>

                <h2>Memories Found:</h2>
                ${data.memories.map(m => `
                    <div>
                        <h3>${m.file_name}</h3>
                        ${m.file_type === 'video' ?
                            `<video src="${m.file_url}" controls width="400"></video>` :
                            `<img src="${m.file_url}" width="400">`
                        }
                        <p>${m.description}</p>
                        <p>People: ${m.people.join(', ')}</p>
                        <p>Similarity: ${m.similarity.toFixed(2)}</p>
                    </div>
                `).join('')}
            `;
        }
    </script>
</body>
</html>
```

---

## Testing Locally Before Deploy

```bash
cd /Users/keshavgoel/ForgetMeNot
uvicorn main:app --host 0.0.0.0 --port 8000

# Test from teammate's HTML (update API_URL to http://localhost:8000)
```

---

## CORS Configuration

Your API already has CORS enabled for all origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For production**, update to specific domain:
```python
allow_origins=["https://your-frontend-domain.com"]
```

---

## Quick Deploy Commands

### Deploy to Render (via GitHub)
```bash
git add requirements.txt render.yaml
git commit -m "Add deployment config"
git push origin main
# Then connect repo on render.com
```

### Deploy to Railway (CLI)
```bash
railway login
railway init
railway up
railway open
```

Your API will be live in ~5 minutes! 🚀
