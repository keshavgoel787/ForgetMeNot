# Running the Complete Pipeline

This guide walks you through running all steps of the ForgetMeNot processing pipeline.

## 🚀 **Quick Start - Run Everything at Once**

Raw Videos/Images → Face Extraction → Name Mapping → AI Context Generation
```

1. **Step 1**: Extract faces → Creates `person_1/`, `person_2/`, etc.
2. **Step 2**: Map names → Renames to `anna/`, `lisa/`, etc.
3. **Step 3**: Generate context → AI analyzes and identifies people

---

## 🚀 **Complete Workflow**

### **Step 1: Extract Faces**

```bash
python 1_extract_faces.py
```

**What it does:**
- Scans all videos/images in `pre_processed/data/memories/`
- Extracts faces from every frame/image
- Clusters similar faces together
- Creates `person_1/`, `person_2/`, `person_3/`... folders

**Output:**
```
pre_processed/data/people/
├── person_1/
│   ├── face_0000.jpg
│   ├── face_0001.jpg
│   └── metadata.json
├── person_2/
└── person_3/
```

**Time:** ~10-30 minutes depending on video count

---

### **Step 2: Convert Names**

**First, edit `names.json`:**

```bash
nano pre_processed/data/people/names.json
```

**Format (EITHER works):**

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

**Then run:**

```bash
python 2_convert_names.py
```

**What it does:**
- Reads your names.json mapping
- Renames `person_1/` → `anna/`
- Merges `person_2/` + `person_7/` → `lisa/`
- Deletes unmapped folders

**Output:**
```
pre_processed/data/people/
├── anna/
├── lisa/
└── bob/
```

**Time:** Instant

---

### **Step 3: Generate Context**

```bash
python 3_generate_context.py
```

**What it does:**
- Loads reference images for each person (anna, lisa, bob)
- Analyzes every video/image with Gemini AI
- Identifies people using face references
- Generates context descriptions with names
- Saves to `context.json` in each memory folder

**Output in each memory folder:**
```json
{
  "memory_context": "...",
  "video1_context": "Anna and Lisa shopping at Target...",
  "video1_people": "anna, lisa",
  "video2_context": "Bob playing basketball...",
  "video2_people": "bob"
}
```

**Time:** ~1-5 minutes per video (depends on API speed)

**Cost:** Uses Gemini API credits

---

## 🎯 **Quick Commands**

Run all steps:

```bash
# Step 1: Extract faces
python 1_extract_faces.py

# Step 2: Edit names.json, then convert
nano pre_processed/data/people/names.json
python 2_convert_names.py

# Step 3: Generate context
python 3_generate_context.py
```

---

## 📁 **Final Structure**

```
pre_processed/data/
├── memories/
│   ├── day in college/
│   │   ├── video1.mp4
│   │   ├── video2.mp4
│   │   └── context.json          ← Generated with names
│   └── ski trip/
│       └── context.json
└── people/
    ├── anna/
    │   ├── face_0000.jpg          ← Reference images
    │   └── metadata.json
    ├── lisa/
    ├── bob/
    └── names.json                 ← Your mapping
```

---

## ⚠️ **Important Notes**

1. **Run in order** - Each step depends on the previous one
2. **Backup first** - Copy your `people/` folder before Step 2
3. **Check names.json** - Make sure it's correct before Step 2
4. **API key required** - Set `GEMINI_API_KEY` in `.env` for Step 3
5. **Be patient** - Step 3 can take a while with many videos

---

## 🔧 **Troubleshooting**

**"unknown" in people detection:**
- The face references might be poor quality
- Try using more/better reference images
- Check if person is actually in your people folders

**Faces merged incorrectly:**
- Adjust clustering tolerance in `memory_to_people.py`
- Re-run Step 1 with different settings

**API errors:**
- Check your Gemini API key
- Verify you have API credits
- Check internet connection

---

## 💡 **Tips**

- **Test first**: Use `test_memory_to_people.py` and `test_text_context_per_memory.py` on small samples
- **Review clustering**: Check person folders before naming them
- **Iterate**: You can re-run Step 2 and 3 without re-doing Step 1
