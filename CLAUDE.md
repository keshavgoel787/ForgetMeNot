# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ForgetMeNot is a HackRU project that manages memory clips (videos) by uploading metadata to Snowflake with associated tags, emotions, and scene labels for retrieval and search.

## Architecture

- **Data Pipeline**: CSV metadata → Python script → Snowflake database
- **Database Table**: `MEMORY_VAULT` in Snowflake stores clip metadata including:
  - Basic info: id (UUID), title, clip_name, description
  - Classification: scene_label, emotion_label
  - Searchable: context_tags (JSON array), clip_url
- **Environment Configuration**: Uses `.env` file for Snowflake credentials (user, password, account, warehouse, database, schema)

## Commands

### Upload metadata to Snowflake
```bash
python upload_to_snowflake.py
```

## Dependencies

The project requires:
- `snowflake-connector-python` for database connection
- `pandas` for CSV processing
- `python-dotenv` for environment variable management

## Environment Setup

Create a `.env` file with the following variables:
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`

## Data Format

The `metadata.csv` file must include these columns:
- `clip_name`: Video filename
- `title`: Memory title
- `description`: Text description
- `scene_label`: Scene type (e.g., beach, stadium, classroom)
- `emotion_label`: Emotional context (e.g., joyful, excited, focused)
- `context_tags`: Python list as string (e.g., `"['outdoors','family','vacation']"`)


## 🧠 **Project Summary: ReMind — An AI Memory Companion for Alzheimer’s Care**

**Overview:**
ReMind is a multimodal AI platform designed to help Alzheimer’s patients reconnect with their memories through intelligent, emotionally aware “memory replays.” It combines retrieval, generation, and empathetic interaction — enabling patients to revisit key life moments while caregivers monitor emotional and cognitive progress.

---

### 🌍 **Problem**

Alzheimer’s patients often struggle with confusion, emotional distress, and disconnection from loved ones. Caregivers lack tools to provide personalized memory stimulation or track changes in cognitive behavior.

### 💡 **Solution**

ReMind uses **AI-driven memory reconstruction** to retrieve, recreate, and narrate personal experiences — turning photos, videos, and stories into immersive, emotional “living memories.”

---

### ⚙️ **System Architecture**

#### 1. **Input Layer (Patient / Therapist)**

* Voice or text input via smart speaker, tablet, or web interface.
* Example: “Show me my trip to Disney with Anna.”

#### 2. **Reasoning Layer — Gemini**

* Parses the query to extract **intent**, **entities**, and **emotion**.
* Generates **semantic SQL** queries for Snowflake and prompts for Veo / ElevenLabs.
* Example output:

  ```json
  {
    "intent": "PlayMemory",
    "entities": ["Anna", "Disney Beach"],
    "emotion": "nostalgic"
  }
  ```

#### 3. **Memory Vault — Snowflake**

* Central repository of all patient data (video clips, images, transcripts, metadata).
* Stores multimodal **embeddings**, emotion labels, and context tags.
* Supports **semantic memory retrieval** using `CORTEX.EMBED_TEXT()` and vector search.
* Example:

  ```sql
  SELECT title, clip_url, description
  FROM MEMORY_VAULT
  ORDER BY VECTOR_COSINE_DISTANCE(
    embedding, SNOWFLAKE.CORTEX.EMBED_TEXT('Disney beach Anna')
  )
  LIMIT 3;
  ```

#### 4. **Generation Layer**

* **Veo (Video-to-Video / Image-to-Video / Text-to-Video)**

  * Recreates scenes or animates static memories into cinematic, nostalgic clips.
  * Example prompt:

    > “Animate this photo into a calm, warm memory — palm trees swaying, soft golden light, hammock gently rocking.”

* **ElevenLabs (Voice Synthesis)**

  * Narrates the memory using a comforting, familiar voice.
  * Example:

    > “You remember that day — the laughter, the sunlight, the feeling of peace.”

#### 5. **Output Layer**

* Delivers personalized video experiences or interactive dialogue.
* Modes:

  * **Play Memory** → displays generated video + narration.
  * **Talk to Memory** → Gemini engages in conversation (“Was I happy that day?”).
* Outputs also log engagement data for caregiver analytics.

---

### 🧩 **Core Pipelines**

| Stage                | Input               | Model/Tool       | Output                |
| -------------------- | ------------------- | ---------------- | --------------------- |
| **Speech to Text**   | Patient voice       | WhisperX         | Query text            |
| **Intent Parsing**   | Query               | Gemini           | Entities + emotion    |
| **Memory Retrieval** | Query text          | Snowflake Cortex | Relevant clips        |
| **Video Generation** | Photo / clip / text | Veo              | “Memory replay” video |
| **Narration**        | Context summary     | ElevenLabs       | Audio voice track     |
| **Playback**         | Video + audio       | Web / App        | Immersive experience  |

---

### 🧱 **Tech Stack**

* **AI Reasoning:** Gemini 1.5 Pro
* **Database + Retrieval:** Snowflake Cortex (CORTEX.EMBED_TEXT, VECTOR_DISTANCE)
* **Video Generation:** Google Veo (Video-to-Video / Image-to-Video / Text-to-Video)
* **Voice Generation:** ElevenLabs API
* **Storage:** Google Cloud Storage (GCS bucket)
* **Frontend:** Streamlit / React (Patient + Caregiver Dashboard)
* **Integration:** Python (Snowflake Connector, Vertex AI, ElevenLabs SDK)

---

### 🎯 **Key Features**

1. **Memory Vault (Snowflake):** Stores and retrieves videos, photos, and transcripts with embeddings.
2. **Context-Aware Retrieval:** Gemini builds natural queries → Snowflake searches semantically.
3. **Memory Reconstruction:** Veo animates stills or transforms clips into “living” videos.
4. **Empathic Narration:** ElevenLabs recreates familiar voices for comforting playback.
5. **Caregiver Dashboard:** Snowflake Streamlit app visualizes emotion trends and engagement metrics.
6. **Automated Updates:** Snowflake Tasks auto-generate embeddings and summaries for new uploads.

---

### ❤️ **Impact**

* Preserves patient identity and emotional continuity.
* Helps caregivers detect early cognitive changes.
* Builds a compassionate bridge between data and human memory.

---

### 🚀 **Hackathon MVP**

* ✅ Query memory by voice: “Show me my Disney trip.”
* ✅ Retrieve clip from Snowflake by embedding similarity.
* ✅ Generate emotional video (Veo) + narration (ElevenLabs).
* ✅ Display “Memory Replay” in UI.
* (Optional) Interactive chat: “What did Anna say that day?”

---

### 🧭 **Future Expansion**

* Emotion tracking over time (LLM summaries).
* Multi-user family memory linking.
* Caregiver alert system for confusion or distress detection.
* Fine-tuned model on personal memory embeddings for lifelong use.

---

### 🔐 **Ethical Considerations**

* All content generated from patient-consented data.
* No external sharing of personal assets.
* Memory playback designed to comfort, not confuse or deceive.

---

**In one sentence:**

> *ReMind is an AI memory companion that helps Alzheimer’s patients relive, understand, and emotionally connect with their past using multimodal retrieval and generation through Gemini, Snowflake, Veo, and ElevenLabs.*
