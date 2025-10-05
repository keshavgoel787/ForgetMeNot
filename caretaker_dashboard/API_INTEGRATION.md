# API Integration Guide

This document explains how the Face Naming page integrates with the ForgetMeNot backend API.

## Overview

The face naming workflow now uses two main API endpoints from the Python FastAPI server:

1. **POST /extract-faces** - Extracts and clusters faces from uploaded memories
2. **POST /generate-context** - Generates AI context with named people

## Architecture

```
User Upload → Extract Faces API → Face Naming UI → Generate Context API → Download Results
```

## Workflow Steps

### 1. Upload Phase
- User uploads a ZIP file containing a `memories` folder with photos/videos
- File is validated on the client side
- State: `processingStage = 'upload'`

### 2. Face Extraction Phase
- ZIP file is sent to `POST /extract-faces`
- Backend extracts faces using face_recognition library
- Faces are clustered into `person_1`, `person_2`, etc.
- Returns a ZIP with 16 sampled faces per person
- Client parses the ZIP and displays face bubbles
- State: `processingStage = 'extracting'` → `'naming'`

### 3. Naming Phase
- User assigns names to each person cluster
- Interactive bubble UI with mouse repulsion physics
- Names are stored in `allAssignments` state object
- Format: `{ "person_1": "John", "person_2": "Jane" }`
- State: `processingStage = 'naming'`

### 4. Context Generation Phase
- After all names are assigned, user clicks "Save Everything"
- Original ZIP + names mapping sent to `POST /generate-context`
- Backend:
  - Re-extracts ALL faces (not sampled)
  - Applies name mappings to person folders
  - Generates AI context for each memory using Gemini
  - Creates `context.json` in each memory folder
- Returns complete annotated ZIP
- Client automatically downloads the result
- State: `processingStage = 'generating'` → `'complete'`

## API Client Functions

### `extractFaces(dataZipFile: File): Promise<Blob>`
Uploads a ZIP file and returns extracted faces.

**Request:**
```typescript
FormData {
  data_zip: File
}
```

**Response:** ZIP blob containing:
```
people/
  person_1/
    face_001.jpg
    face_002.jpg
    ...
  person_2/
    face_001.jpg
    ...
```

### `generateContext(dataZipFile: File, namesMapping: Record<string, string>): Promise<Blob>`
Generates context with named people.

**Request:**
```typescript
FormData {
  data_zip: File,
  names_json: Blob (JSON)
}
```

**Names JSON Format:**
```json
{
  "John": "person_1,person_3",
  "Jane": "person_2"
}
```

**Response:** ZIP blob containing:
```
memories/
  memory_001/
    photo1.jpg
    photo2.jpg
    context.json
  memory_002/
    ...
people/
  John/
    face_001.jpg
    ...
  Jane/
    face_001.jpg
    ...
```

### `parseExtractedFacesZip(zipBlob: Blob): Promise<{folders: Array<...>}>`
Parses the extracted faces ZIP and converts images to data URLs for display.

### `downloadBlob(blob: Blob, filename: string): void`
Triggers a browser download for a blob.

## State Management

### Processing Stages
```typescript
type ProcessingStage = 
  | 'upload'      // Initial upload screen
  | 'extracting'  // Calling extract-faces API
  | 'naming'      // Interactive naming UI
  | 'generating'  // Calling generate-context API
  | 'complete'    // Success screen
  | 'error';      // Error state
```

### Key State Variables
- `uploadedFile: File | null` - Original uploaded ZIP (kept for generate-context)
- `extractedZipBlob: Blob | null` - Result from extract-faces API
- `folders: Folder[]` - Parsed person folders with image URLs
- `allAssignments: { [folderName: string]: string }` - Name assignments
- `processingProgress: string` - Current progress message
- `errorMessage: string` - Error details if any

## Environment Configuration

Set the API base URL in your environment:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`.

## Error Handling

All API calls are wrapped in try-catch blocks:
- Network errors → Display error message, stay in error state
- Validation errors → Display specific error from API
- Processing errors → Allow user to retry or go back

## UI Features

### Upload Screen
- Drag & drop zone for ZIP files
- File validation
- Instructions for users
- Error display

### Extracting/Generating Screen
- Animated loading spinner
- Progress messages
- Animated progress bar

### Naming Screen
- Interactive bubble physics
- Mouse repulsion effect
- Name input with Enter key support
- Navigation between people
- Progress indicator

### Summary Screen
- Visual review of all assignments
- Expandable name groups
- Pan/scroll navigation
- Final save button

### Complete Screen
- Success animation
- Option to process another file
- Auto-download of results

## Dependencies

```json
{
  "jszip": "^3.x.x"  // For parsing ZIP files on client
}
```

## Backend Requirements

The Python FastAPI server must be running with:
- `face_recognition` library
- `opencv-python`
- `scikit-learn`
- `GEMINI_API_KEY` environment variable

See `api_server/main.py` for full backend implementation.

## Testing

To test without the backend:
1. The upload screen will show errors if API is unavailable
2. Mock data can be added for development
3. Check browser console for detailed error messages

## Future Enhancements

- [ ] Progress tracking with websockets
- [ ] Batch processing multiple ZIP files
- [ ] Preview context.json before download
- [ ] Edit names after generation
- [ ] Save sessions for later completion
