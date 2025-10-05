# API Integration Documentation

## Overview
The ForgetMeNot frontend integrates with two main API endpoints:
1. **GET `/patient/experience/topic/{topic}`** - Fetches initial experience when a topic is selected
2. **POST `/patient/query`** - Sends patient audio queries and receives personalized responses

## Implementation Details

### 1. Initial Experience Endpoint (GET)

#### Endpoint
- **URL**: `https://forgetmenot-p4pb.onrender.com/patient/experience/topic/{topic}`
- **Method**: GET
- **Topic Format**: **MUST be capitalized** (e.g., `College`, `Avery`, `Disney`)
- **Example**: `GET /patient/experience/topic/College`

### 2. Patient Query Endpoint (POST)

#### Endpoint
- **URL**: `https://forgetmenot-p4pb.onrender.com/patient/query`
- **Method**: POST
- **Content-Type**: `multipart/form-data`
- **Example**: 
```bash
curl -X POST https://forgetmenot-p4pb.onrender.com/patient/query \
  -F "audio_file=@patient_audio.webm" \
  -F "topic=College"
```

#### Request Format
- **Form Data**:
  - `audio_file`: Audio file (webm format with opus codec)
  - `topic`: Capitalized topic name (e.g., "College", "Avery")

### Response Format
```json
{
    "topic": "College",
    "text": "Here are your memories about College...",
    "displayMode": "4-pic",
    "media": [
        "https://storage.googleapis.com/forgetmenot-videos/day%20in%20college/saladfoodpic.png",
        "https://storage.googleapis.com/forgetmenot-videos/ski%20trip/Screenshot.png",
        "https://storage.googleapis.com/forgetmenot-videos/football%20trip/Football_trip_7.png",
        "https://storage.googleapis.com/forgetmenot-videos/ski%20trip/Screenshot2.png"
    ]
}
```

**Error Response:**
```json
{
    "detail": "No experience found for topic: sometopic"
}
```

### Display Modes
- `3-pic`: Three overlapping photos
- `4-pic`: Four overlapping photos
- `5-pic`: Five overlapping photos
- `video`: Horizontal video
- `vertical-video`: Vertical video

## How It Works

### Complete User Flow

#### 1. Topic Selection
1. **User clicks a topic** (e.g., "College", "Avery", "Disney")
2. **Microphone permission requested** - Browser prompts for microphone access
3. **Topic stored as lowercase** - All topics are normalized to lowercase internally (`college`, `avery`, `disney`)
4. **API fetch is triggered** - `fetchExperienceByTopic(topic)` is called with capitalized topic
5. **First memory displayed** - The API response is shown with images/video and narration plays

#### 2. Audio Recording & Query Flow
1. **User clicks microphone button** - Starts audio recording
2. **Recording indicator shown** - Red pulsing circle and waveform animation
3. **User speaks their question** - Audio is captured in WebM format
4. **User clicks microphone again** - Stops recording
5. **Audio sent to API** - POST request to `/patient/query` with audio file and topic
6. **Response processed** - New memory displayed based on 6-mode classification:
   - `4-pic`: 4 images + narration
   - `3-pic`: 3 images + narration
   - `5-pic`: 5 images + narration
   - `video`: Horizontal video + narration
   - `vertical-video`: Vertical video + narration
   - `agent`: Conversational lip-sync video (no text)
7. **Repeat** - User can continue asking questions within the same topic

#### 3. Topic Switching
- When switching topics, new API call to `/patient/experience/topic/{newTopic}`
- Recording state reset
- New topic context established

### Topic Format Handling
- **UI Display**: Capitalized topic names (e.g., "Avery", "College") for user-friendly presentation
- **Internal Storage**: Lowercase topics (e.g., "avery", "college") for consistency
- **Mock Data**: Lowercase topics in JSON files (e.g., `"topic": "college"`)
- **Mock Data Comparisons**: Case-insensitive to ensure compatibility
- **API Calls**: Capitalized format (e.g., "College", "Avery") - automatically converted before API request

### State Management
- `apiMemory`: Stores the memory fetched from the API
- `useApiMemory`: Boolean flag to indicate if API memory should be used
- `memoriesForDisplay`: Combined array of [API memory, ...mock memories]
- `isRecording`: Boolean flag indicating if audio is being recorded
- `hasRecordingPermission`: Boolean flag for microphone permission status
- `mediaRecorderRef`: Reference to MediaRecorder instance
- `audioChunksRef`: Reference to store recorded audio chunks

### Audio Recording Implementation

#### Microphone Permission
- **When**: Requested when user first selects a topic
- **How**: Uses `navigator.mediaDevices.getUserMedia({ audio: true })`
- **Fallback**: Alert shown if permission denied

#### Recording Process
1. **Start Recording**:
   ```typescript
   const mediaRecorder = new MediaRecorder(stream, {
     mimeType: 'audio/webm;codecs=opus'
   });
   mediaRecorder.start();
   ```

2. **Capture Audio**:
   - Audio chunks stored in `audioChunksRef.current`
   - WebM format with Opus codec for optimal browser compatibility

3. **Stop & Send**:
   ```typescript
   mediaRecorder.stop(); // Triggers onstop event
   const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
   // Send to /patient/query endpoint
   ```

#### UI Indicators
- **Idle State**: White microphone icon, "Click to speak"
- **Recording State**: 
  - Red pulsing circle
  - Animated red waveform
  - Text: "Recording... (click to send)"
- **Playing State**: "Remembering..."

### Fallback Behavior
If the API call fails:
- Falls back to local mock data
- Console logs the error for debugging
- User experience continues without interruption

### Code Structure

#### Main Function
```typescript
const fetchExperienceByTopic = async (topic: string): Promise<Memory | null> => {
  // API expects capitalized topic names (e.g., "Avery", "College")
  const capitalizedTopic = topic.charAt(0).toUpperCase() + topic.slice(1).toLowerCase();
  const response = await fetch(`https://forgetmenot-p4pb.onrender.com/patient/experience/topic/${capitalizedTopic}`);
  
  const data = await response.json();
  
  // Check for error responses
  if (data.detail) {
    return null;
  }
  
  // Transform API response to Memory format
  return {
    id: `api-${topic.toLowerCase()}`,
    topic: data.topic || topic,
    title: data.title,
    text: data.text,
    displayMode: data.displayMode || '4-pic',
    media: data.media || []
  };
}
```

#### Audio Query Function
```typescript
const sendAudioQuery = async (audioBlob: Blob) => {
  const formData = new FormData();
  formData.append('audio_file', audioBlob, 'patient_audio.webm');
  formData.append('topic', capitalizedTopic);
  
  const response = await fetch('https://forgetmenot-p4pb.onrender.com/patient/query', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  
  // Update display with new content
  setDisplayMode(data.displayMode || '4-pic');
  setCurrentMedia(data.media);
  fetchAndPlayAudio(data.text);
}
```

#### Topic Click Handler
```typescript
const handleTopicClick = async (topic: string) => {
  // Request microphone permission
  if (!hasRecordingPermission) {
    await requestMicrophonePermission();
  }
  
  // Fetch initial experience from API
  const apiMemoryData = await fetchExperienceByTopic(topic);
  
  if (apiMemoryData) {
    setApiMemory(apiMemoryData);
    setUseApiMemory(true);
    // Display API memory
  } else {
    // Fallback to mock data
  }
}
```

## Testing

### Test the Complete Flow

#### 1. Initial Setup
1. Open browser console (F12) to see debug logs
2. Navigate to the application

#### 2. Topic Selection
1. Click on any topic button (Avery, College, Disney, etc.)
2. **Allow microphone permission** when browser prompts
3. Watch console for:
   - `🎤 Requesting microphone permission...`
   - `✅ Microphone permission granted`
   - `🔵 Fetching experience from API: ...`
   - `✅ API response data: {...}`
4. Experience should load with images/video and narration plays

#### 3. Audio Recording & Query
1. **Click microphone button** to start recording
   - Watch for: `🎤 Starting audio recording...`
   - UI should show red pulsing circle
   - Waveform should animate in red
   - Text should show "Recording... (click to send)"
2. **Speak your question** (e.g., "Tell me more about college")
3. **Click microphone again** to stop and send
   - Watch for: `⏹️ Stopping recording...`
   - Watch for: `📤 Sending audio query for topic: ...`
   - Watch for: `✅ Patient query response: {...}`
4. New experience should load based on your question
5. **Repeat**: Continue asking questions about the same topic

#### 4. Topic Switching
1. Click a different topic button
2. Process repeats with new API call
3. Recording state resets

### Expected Behavior
- ✅ Microphone permission requested on first topic selection
- ✅ Initial topic selection fetches from GET API
- ✅ Display shows API content (images/video + text)
- ✅ Text-to-speech plays the API response narration
- ✅ Mic button starts/stops audio recording
- ✅ Audio sent to POST /patient/query endpoint
- ✅ Response classified into 6 display modes
- ✅ Switching topics triggers new GET API fetch
- ✅ Graceful fallback to mock data if API fails

### Console Log Guide
- 🔵 **Blue** - API calls and info
- ✅ **Green checkmark** - Success
- ❌ **Red X** - Errors
- ⚠️ **Warning** - Fallbacks or warnings
- 📁 **Folder** - Mock data usage
- 🎤 **Microphone** - Recording events
- 📤 **Upload** - Sending data
- 📥 **Download** - Receiving data

## Files Modified
- `/client_frontend/src/App.tsx` - Main application logic with API integration

## Environment
- **Production API**: `https://forgetmenot-p4pb.onrender.com`
- **Frontend**: React + TypeScript + Vite
