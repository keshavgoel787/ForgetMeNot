/**
 * API Client for ForgetMeNot Backend
 * Handles communication with the Python FastAPI server
 * 
 * NOTE: API calls are currently commented out for graceful fallback.
 * The app will use mock data when API is unavailable.
 */

// API URLs for external services
const EXPERIENCE_API_URL = process.env.NEXT_PUBLIC_EXPERIENCE_API_URL || 'https://forgetmenot-p4pb.onrender.com';
const FACE_EXTRACTION_API_URL = process.env.NEXT_PUBLIC_FACE_API_URL || 'https://forgetmenot-eq7i.onrender.com';

// Demo mode: Use hardcoded mock data for face extraction and saving
const USE_MOCK_DATA = false; // Set to false to enable real API calls
const USE_MOCK_FACES = false; // Set to false to enable real face extraction API

export interface ExtractFacesResponse {
  success: boolean;
  faceZipUrl?: string;
  error?: string;
}

export interface GenerateContextResponse {
  success: boolean;
  outputZipUrl?: string;
  error?: string;
}

export interface ApiError {
  detail: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

export interface Memory {
  event_name: string;
  file_name: string;
  file_type: string;
  description: string;
  faces: string[];
  event_summary: string;
  file_url: string;
  similarity: number;
}

export interface Scene {
  scene: string;
  memories: Memory[];
  ai_narrative: string;
}

export interface CreateExperienceRequest {
  title: string;
  general_context: string;
  scenes: string[];
  top_k?: number;
}

export interface CreateExperienceResponse {
  experience_id: string;
  title: string;
  general_context: string;
  scenes: Scene[];
  overall_narrative: string;
  total_memories: number;
  created_at: string;
  patient_url: string;
}

/**
 * Upload data ZIP and extract faces (16 samples per face set)
 * Endpoint: POST /extract-faces
 */
export async function extractFaces(dataZipFile: File, useMock: boolean = false): Promise<Blob> {
  // Use mock data for demo
  if (useMock || USE_MOCK_FACES) {
    console.log('🎭 Demo Mode: Using mock data for face extraction');
    return createMockExtractedFacesZip();
  }

  // Real API call to external face extraction service
  try {
    const formData = new FormData();
    formData.append('data_zip', dataZipFile);

    const response = await fetch(`${FACE_EXTRACTION_API_URL}/api/extract-faces`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Return the ZIP blob
    return await response.blob();
  } catch (error) {
    console.warn('API unavailable, falling back to mock data:', error);
    return createMockExtractedFacesZip();
  }
}

/**
 * Save named faces mapping to backend
 * Endpoint: POST /api/save-faces
 * 
 * @param namesMapping - Object mapping face_set_X to actual names (e.g., {"face_set_1": "John", "face_set_2": "Jane"})
 */
export async function saveNamedFaces(
  namesMapping: Record<string, string>,
  useMock: boolean = false
): Promise<void> {
  // Use mock data for demo
  if (useMock || USE_MOCK_FACES) {
    console.log('🎭 Demo Mode: Names saved locally:', namesMapping);
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    return;
  }

  // Real API call to save named faces
  try {
    // Convert names mapping to the expected format: { "John": "face_set_1,face_set_3", "Jane": "face_set_2" }
    const invertedMapping: Record<string, string> = {};
    Object.entries(namesMapping).forEach(([faceSetId, name]) => {
      if (name && name.trim()) {
        if (!invertedMapping[name]) {
          invertedMapping[name] = faceSetId;
        } else {
          invertedMapping[name] += `,${faceSetId}`;
        }
      }
    });

    const response = await fetch(`${FACE_EXTRACTION_API_URL}/api/save-faces`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(invertedMapping),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    console.log('Named faces saved successfully');
  } catch (error) {
    console.error('Error saving named faces:', error);
    throw error;
  }
}

/**
 * Helper to download a blob as a file
 */
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Create mock extracted faces ZIP for testing
 */
async function createMockExtractedFacesZip(): Promise<Blob> {
  const JSZip = (await import('jszip')).default;
  const zip = new JSZip();
  
  // Create mock face set folders with placeholder images
  const mockFaceSets = [
    { folder: 'face_set_1', count: 16 },
    { folder: 'face_set_2', count: 16 },
    { folder: 'face_set_3', count: 16 },
  ];
  
  for (const faceSet of mockFaceSets) {
    for (let i = 1; i <= faceSet.count; i++) {
      // Create a simple colored square as placeholder
      const canvas = document.createElement('canvas');
      canvas.width = 100;
      canvas.height = 100;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Different color for each face set
        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1'];
        const faceSetIndex = parseInt(faceSet.folder.split('_')[2]) - 1;
        ctx.fillStyle = colors[faceSetIndex % colors.length];
        ctx.fillRect(0, 0, 100, 100);
        
        // Add face number
        ctx.fillStyle = 'white';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${i}`, 50, 55);
      }
      
      const blob = await new Promise<Blob>((resolve) => {
        canvas.toBlob((b) => resolve(b!), 'image/jpeg', 0.8);
      });
      
      zip.file(`face/${faceSet.folder}/face_${String(i).padStart(3, '0')}.jpg`, blob);
    }
  }
  
  return await zip.generateAsync({ type: 'blob' });
}


/**
 * Create a new experience
 * Endpoint: POST /experiences/create
 */
export async function createExperience(
  request: CreateExperienceRequest
): Promise<CreateExperienceResponse> {
  try {
    const response = await fetch(`${EXPERIENCE_API_URL}/experiences/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating experience:', error);
    throw error;
  }
}

/**
 * Helper to extract ZIP blob and parse folder structure
 */
export async function parseExtractedFacesZip(zipBlob: Blob): Promise<{
  folders: Array<{
    name: string;
    images: string[];
    imageUrls: string[];
  }>;
}> {
  // This would require a ZIP parsing library on the client side
  // For now, we'll return a structure that can be populated
  // In production, consider using jszip library
  
  const JSZip = (await import('jszip')).default;
  const zip = await JSZip.loadAsync(zipBlob);
  
  const folders: Record<string, { name: string; images: string[]; imageUrls: string[] }> = {};
  
  // Parse ZIP structure
  for (const [filename, file] of Object.entries(zip.files)) {
    if (file.dir) continue;
    
    // Extract face set folder name (e.g., "face/face_set_1/face_001.jpg" -> "face_set_1")
    const parts = filename.split('/');
    if (parts.length >= 2) {
      const folderName = parts[parts.length - 2];
      const imageName = parts[parts.length - 1];
      
      if (folderName.startsWith('face_set_') && imageName.match(/\.(jpg|jpeg|png)$/i)) {
        if (!folders[folderName]) {
          folders[folderName] = {
            name: folderName,
            images: [],
            imageUrls: [],
          };
        }
        
        // Convert image to data URL
        const blob = await file.async('blob');
        const dataUrl = URL.createObjectURL(blob);
        
        folders[folderName].images.push(imageName);
        folders[folderName].imageUrls.push(dataUrl);
      }
    }
  }
  
  return {
    folders: Object.values(folders),
  };
}
