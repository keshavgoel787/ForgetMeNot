# Memory to People Extraction

Automatically detect, extract, and cluster people from all your memory videos and images using face recognition and machine learning.

## What It Does

This script:
1. **Extracts faces** from all images and video frames in your memory folders
2. **Clusters faces** using facial recognition to group the same person together
3. **Creates person folders** (`person_1`, `person_2`, etc.) with all their appearances
4. **Generates metadata** showing which memories each person appears in

## Features

- 👤 **Face Detection**: Uses `face_recognition` library for accurate face detection
- 🧩 **Smart Clustering**: DBSCAN algorithm groups similar faces into same person
- 📊 **Comprehensive Metadata**: Tracks source files, memories, and appearance counts
- 🎥 **Video Support**: Samples video frames at 2 FPS for face extraction
- 📁 **Organized Output**: Each person gets their own folder with all face images

## Setup

### 1. Install Additional Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate

# Install the updated requirements
pip install -r requirements.txt
```

**Note**: `face-recognition` requires `dlib` which may need additional system dependencies:

**On Ubuntu/Debian:**
```bash
sudo apt-get install cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
```

**On macOS:**
```bash
brew install cmake
```

### 2. Run the Script

```bash
# Make sure you're in the processing_script directory
cd processing_script

# Activate virtual environment
source venv/bin/activate

# Run the people extractor
python memory_to_people.py
```

## Output Structure

After running, you'll have a new `people/` folder:

```
pre_processed/data/
├── memories/
│   ├── day in college/
│   ├── disney trip/
│   ├── football trip/
│   └── ski trip/
└── people/              # NEW!
    ├── person_1/        # Person who appears most frequently
    │   ├── face_0000.jpg
    │   ├── face_0001.jpg
    │   ├── face_0002.jpg
    │   └── metadata.json
    ├── person_2/
    │   ├── face_0000.jpg
    │   ├── face_0001.jpg
    │   └── metadata.json
    └── person_3/
        └── ...
```

### Example metadata.json

```json
{
  "person_id": 1,
  "total_appearances": 45,
  "memories": [
    "day in college",
    "disney trip",
    "ski trip"
  ],
  "sources": [
    {
      "image_file": "face_0000.jpg",
      "memory": "day in college",
      "source_file": "walkingwithfriend.mp4",
      "source_type": "video"
    },
    {
      "image_file": "face_0001.jpg",
      "memory": "ski trip",
      "source_file": "isa sung ski-1.mp4",
      "source_type": "video"
    }
  ]
}
```

## How It Works

### 1. Face Extraction
- **Images**: Detects all faces in each image
- **Videos**: Samples frames every 2 FPS and extracts faces

### 2. Face Encoding
- Creates 128-dimensional face encodings for each detected face
- These encodings capture unique facial features

### 3. Clustering
- Uses **DBSCAN** clustering algorithm
- Groups similar face encodings together
- Tolerance parameter (`eps=0.5`) controls strictness
  - Lower = more strict (more distinct people)
  - Higher = more lenient (fewer people)

### 4. Organization
- People ranked by number of appearances
- `person_1` = most frequent, etc.
- Each person folder contains all their face images

## Adjusting Clustering

If you find clustering too strict or too lenient, edit the tolerance in `memory_to_people.py`:

```python
# Line ~247 in the script
clustered_faces = self.cluster_faces(tolerance=0.5)  # Adjust this value

# Lower (e.g., 0.4) = stricter, more people
# Higher (e.g., 0.6) = lenient, fewer people
```

## Next Steps

After running this script, you can:
1. **Review person folders** to verify clustering accuracy
2. **Manually label people** by renaming folders (e.g., `person_1` → `sarah`)
3. **Use as reference** for the Gemini API to identify people in videos
4. **Build a face recognition system** for your personal memories

## Performance Notes

- Processing time depends on number of videos/images and length
- Video processing is the most time-intensive
- Face detection uses HOG model (faster but less accurate than CNN)
- For better accuracy but slower speed, change `model="hog"` to `model="cnn"` in the script

## Troubleshooting

**"dlib not found" error:**
- Install system dependencies (see Setup section)
- May need to compile dlib from source on some systems

**Too many/few people detected:**
- Adjust the `tolerance` parameter in clustering
- Lower value = more people, higher value = fewer people

**Out of memory:**
- Process fewer videos at once
- Reduce `fps_sample` parameter (sample fewer frames per second)

**Slow processing:**
- Reduce video sampling rate (`fps_sample`)
- Skip very long videos
- Use HOG model instead of CNN

## Dependencies

- `face-recognition` - Face detection and encoding
- `opencv-python` - Video frame extraction
- `scikit-learn` - DBSCAN clustering algorithm
- `numpy` - Numerical operations
- `Pillow` - Image processing
