# Mock Data Setup Guide

The Face Naming application now works gracefully without a backend API by using mock data.

## Current Configuration

**API calls are currently DISABLED** and the app uses mock data for demonstration.

### Toggle Between Mock and Real API

Edit `/src/lib/api-client.ts`:

```typescript
const USE_MOCK_DATA = true;  // Set to false to enable real API calls
```

- `true` - Uses mock data (current setting)
- `false` - Attempts real API calls, falls back to mock if unavailable

## Mock Data Features

### 1. Extract Faces Mock Data

When you upload a ZIP file, the app generates:
- **3 person folders** (`person_1`, `person_2`, `person_3`)
- **16 face images per person** (colored squares with numbers)
- Each person has a unique color:
  - Person 1: Red (#FF6B6B)
  - Person 2: Teal (#4ECDC4)
  - Person 3: Blue (#45B7D1)

### 2. Generate Context Mock Data

After naming people, the app generates:
- **3 mock memories** (`memory_001`, `memory_002`, `memory_003`)
- **context.json** for each memory with:
  - Memory ID
  - People identified (from your names)
  - Random people count and image count
  - AI-generated description
  - Timestamp
- **Named people folders** with 5 face images each
- **Placeholder images** for each memory

## How It Works

### Graceful Fallback Strategy

```
1. Check USE_MOCK_DATA flag
   ├─ If true → Use mock data immediately
   └─ If false → Try API call
       ├─ Success → Use API response
       └─ Failure → Fall back to mock data
```

### Mock Data Generation

All mock data is generated client-side using:
- **Canvas API** - Creates colored placeholder images
- **JSZip** - Packages files into ZIP format
- **Blob API** - Handles file downloads

## User Experience

### Visual Indicators

1. **Upload Screen**: Blue info box shows "Demo Mode" notice
2. **Processing Screens**: Progress messages include "(using mock data)"
3. **Complete Screen**: Success alert mentions "Demo mode: Mock data was used"
4. **Console Logs**: All API calls log whether using mock or real data

### Testing the Workflow

1. Go to `/face-naming` page
2. Upload ANY ZIP file (content doesn't matter in mock mode)
3. Click "Extract Faces"
4. See 3 person folders with colored face bubbles
5. Name each person
6. Click "Save Everything"
7. Download the annotated ZIP with your names

## Mock ZIP Contents

### After Extract Faces
```
people/
  person_1/
    face_001.jpg  (red square with "1")
    face_002.jpg  (red square with "2")
    ...
    face_016.jpg  (red square with "16")
  person_2/
    face_001.jpg  (teal square with "1")
    ...
  person_3/
    face_001.jpg  (blue square with "1")
    ...
```

### After Generate Context
```
memories/
  memory_001/
    context.json
    photo.jpg
  memory_002/
    context.json
    photo.jpg
  memory_003/
    context.json
    photo.jpg
people/
  [YourName1]/
    face_001.jpg
    face_002.jpg
    ...
    face_005.jpg
  [YourName2]/
    face_001.jpg
    ...
```

### Sample context.json
```json
{
  "memory_id": "memory_001",
  "people_identified": ["John", "Jane"],
  "people_count": 2,
  "image_count": 8,
  "description": "A memory featuring John, Jane.",
  "generated_at": "2025-10-05T03:32:55.000Z"
}
```

## Enabling Real API

To use the actual Python backend:

1. **Start the backend server**:
   ```bash
   cd api_server
   python main.py
   ```

2. **Set environment variable** (optional):
   ```bash
   # .env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Disable mock data**:
   ```typescript
   // src/lib/api-client.ts
   const USE_MOCK_DATA = false;
   ```

4. **Restart Next.js dev server**:
   ```bash
   npm run dev
   ```

## Error Handling

The app handles errors gracefully:

- **Network errors** → Falls back to mock data
- **API unavailable** → Falls back to mock data
- **Invalid responses** → Falls back to mock data
- **All errors logged** → Check browser console for details

## Benefits of Mock Data

✅ **No backend required** - Test UI without Python server  
✅ **Fast development** - Instant responses, no waiting  
✅ **Reliable testing** - Consistent data every time  
✅ **Demo-ready** - Show the app without infrastructure  
✅ **Offline capable** - Works without internet  

## Limitations

⚠️ **No real face detection** - Uses placeholder images  
⚠️ **No AI context** - Generates simple descriptions  
⚠️ **Fixed person count** - Always creates 3 people  
⚠️ **Random assignments** - People in memories are random  

## Troubleshooting

### Mock data not working?
- Check browser console for errors
- Ensure jszip is installed: `npm install jszip`
- Clear browser cache and reload

### Want to test real API?
- Verify backend is running: `curl http://localhost:8000`
- Check CORS settings in backend
- Set `USE_MOCK_DATA = false`

### Images not displaying?
- Check browser console for blob URL errors
- Ensure Canvas API is supported
- Try a different browser

## Code Structure

### API Client (`src/lib/api-client.ts`)
- `extractFaces()` - Main API call with fallback
- `generateContext()` - Context generation with fallback
- `createMockExtractedFacesZip()` - Mock face extraction
- `createMockAnnotatedZip()` - Mock context generation
- `parseExtractedFacesZip()` - ZIP parsing utility

### Face Naming Page (`src/app/face-naming/page.tsx`)
- Handles all processing stages
- Shows appropriate UI for mock mode
- Manages state and error handling

## Future Enhancements

- [ ] Add more mock person variations
- [ ] Generate more realistic face images
- [ ] Configurable mock data settings
- [ ] Mock data presets (small/medium/large datasets)
- [ ] Simulate API delays for realistic testing
