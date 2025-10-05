# Face Extraction API Endpoint

## Overview

This API endpoint extracts faces from uploaded images/videos, clusters them by person, and returns a ZIP file with organized face folders.

## Endpoint

**POST** `/api/extract-faces`

## Request

### Content-Type
`multipart/form-data`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_zip` | File (binary) | Yes | ZIP file containing a 'memories' folder with images/videos |

### Example Request

```bash
curl -X POST http://localhost:3000/api/extract-faces \
  -F "data_zip=@/path/to/your/memories.zip"
```

```javascript
const formData = new FormData();
formData.append('data_zip', fileInput.files[0]);

const response = await fetch('/api/extract-faces', {
  method: 'POST',
  body: formData,
});

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'extracted_faces.zip';
a.click();
```

## Response

### Success (200)

**Content-Type:** `application/zip`

**Content-Disposition:** `attachment; filename="extracted_faces.zip"`

The response is a ZIP file containing folders named `person_1`, `person_2`, etc., each with up to 16 face images.

**ZIP Structure:**
```
extracted_faces.zip
├── person_1/
│   ├── 1.jpg
│   ├── 2.jpg
│   └── ... (up to 16 images)
├── person_2/
│   ├── 1.jpg
│   ├── 2.jpg
│   └── ... (up to 16 images)
└── person_N/
    └── ...
```

### Error Responses

#### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "data_zip"],
      "msg": "data_zip file is required",
      "type": "value_error"
    }
  ]
}
```

**Possible error messages:**
- `"data_zip file is required"` - No file was uploaded
- `"No memories folder found in ZIP"` - The uploaded ZIP doesn't contain a 'memories' folder
- `"No faces detected in uploaded images"` - No faces were found in the images

#### 500 Internal Server Error

```json
{
  "detail": [
    {
      "loc": ["server"],
      "msg": "Internal server error",
      "type": "server_error"
    }
  ]
}
```

## Requirements

### Python Dependencies

This endpoint requires Python 3 with the following libraries:

```bash
pip install face_recognition opencv-python numpy scikit-learn
```

**Note:** The `face_recognition` library requires:
- CMake
- dlib

**Installation on macOS:**
```bash
brew install cmake
pip install dlib
pip install face_recognition opencv-python numpy scikit-learn
```

**Installation on Ubuntu/Debian:**
```bash
sudo apt-get install cmake python3-dev
pip install dlib
pip install face_recognition opencv-python numpy scikit-learn
```

### Node.js Dependencies

Already included in `package.json`:
- `adm-zip` - ZIP file handling

## How It Works

1. **Upload Processing**: The endpoint receives a ZIP file via multipart form data
2. **Extraction**: Images are extracted from the 'memories' folder within the ZIP
3. **Face Detection**: Python's `face_recognition` library detects faces in each image
4. **Face Encoding**: Each detected face is converted to a 128-dimensional encoding
5. **Clustering**: DBSCAN algorithm clusters similar faces together (same person)
6. **Sampling**: Up to 16 random faces are sampled from each cluster
7. **ZIP Creation**: Clustered faces are organized into `person_X` folders and zipped
8. **Response**: The ZIP file is returned to the client

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)

## Limitations

- **Video Support**: Currently only processes images. Video frame extraction requires additional implementation
- **Processing Time**: Large ZIP files with many images may take several minutes to process
- **Memory Usage**: Processing is memory-intensive for large datasets
- **Python Dependency**: Requires Python 3 with face_recognition library installed on the server

## Production Considerations

For production deployment, consider:

1. **Separate Microservice**: Deploy face extraction as a separate Python microservice
2. **Queue System**: Use a job queue (Redis, RabbitMQ) for async processing
3. **Progress Tracking**: Implement WebSocket or polling for progress updates
4. **Cloud Functions**: Use AWS Lambda, Google Cloud Functions, or Azure Functions
5. **GPU Acceleration**: Use GPU-enabled instances for faster face detection
6. **Caching**: Cache face encodings to avoid reprocessing

## Alternative Implementation

If Python dependencies are not available, consider:

1. **Client-side Processing**: Use face-api.js in the browser
2. **Third-party APIs**: Use AWS Rekognition, Google Vision API, or Azure Face API
3. **Docker Container**: Package Python dependencies in a Docker container

## Testing

```bash
# Create a test ZIP file
mkdir -p test_data/memories
cp your_images/*.jpg test_data/memories/
zip -r test_memories.zip test_data/

# Test the endpoint
curl -X POST http://localhost:3000/api/extract-faces \
  -F "data_zip=@test_memories.zip" \
  -o extracted_faces.zip

# Extract and verify
unzip extracted_faces.zip
ls -R person_*
```

## Troubleshooting

### "Python not found" error
Ensure Python 3 is installed and accessible via `python3` command.

### "face_recognition module not found"
Install the required Python packages:
```bash
pip install face_recognition opencv-python numpy scikit-learn
```

### "No faces detected"
- Ensure images contain visible faces
- Check image quality and resolution
- Verify the 'memories' folder exists in the ZIP

### Memory errors
- Reduce the number of images in the ZIP
- Increase server memory allocation
- Process images in batches
