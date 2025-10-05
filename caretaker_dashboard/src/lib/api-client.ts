/**
 * API Client for ForgetMeNot Backend
 * Handles communication with the Python FastAPI server
 * 
 * NOTE: API calls are currently commented out for graceful fallback.
 * The app will use mock data when API is unavailable.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const USE_MOCK_DATA = true; // Set to false to enable real API calls

export interface ExtractFacesResponse {
  success: boolean;
  peopleZipUrl?: string;
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

/**
 * Upload data ZIP and extract faces (16 samples per person)
 * Endpoint: POST /extract-faces
 */
export async function extractFaces(dataZipFile: File): Promise<Blob> {
  // Use mock data if API is disabled or unavailable
  if (USE_MOCK_DATA) {
    console.log('Using mock data for face extraction (API disabled)');
    return createMockExtractedFacesZip();
  }

  // COMMENTED OUT: Real API call to prevent accidental usage
  /*
  try {
    const formData = new FormData();
    formData.append('data_zip', dataZipFile);

    const response = await fetch(`${API_BASE_URL}/extract-faces`, {
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
  */
  
  // Always use mock data when API calls are commented out
  console.log('API calls are commented out, using mock data');
  return createMockExtractedFacesZip();
}

/**
 * Generate context with people names
 * Endpoint: POST /generate-context
 * 
 * @param dataZipFile - Original memories ZIP file
 * @param namesMapping - Object mapping person_X to actual names (e.g., {"person_1": "John", "person_2": "Jane"})
 */
export async function generateContext(
  dataZipFile: File,
  namesMapping: Record<string, string>
): Promise<Blob> {
  // Use mock data if API is disabled or unavailable
  if (USE_MOCK_DATA) {
    console.log('Using mock data for context generation (API disabled)');
    console.log('Names mapping:', namesMapping);
    return createMockAnnotatedZip(namesMapping);
  }

  // COMMENTED OUT: Real API call to prevent accidental usage
  /*
  try {
    const formData = new FormData();
    formData.append('data_zip', dataZipFile);
    
    // Convert names mapping to the expected format: { "John": "person_1,person_3", "Jane": "person_2" }
    const invertedMapping: Record<string, string> = {};
    Object.entries(namesMapping).forEach(([personId, name]) => {
      if (name && name.trim()) {
        if (!invertedMapping[name]) {
          invertedMapping[name] = personId;
        } else {
          invertedMapping[name] += `,${personId}`;
        }
      }
    });
    
    // Create JSON blob for names_json
    const namesJsonBlob = new Blob([JSON.stringify(invertedMapping)], { type: 'application/json' });
    formData.append('names_json', namesJsonBlob, 'names.json');

    const response = await fetch(`${API_BASE_URL}/generate-context`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Return the complete annotated ZIP blob
    return await response.blob();
  } catch (error) {
    console.warn('API unavailable, falling back to mock data:', error);
    return createMockAnnotatedZip(namesMapping);
  }
  */
  
  // Always use mock data when API calls are commented out
  console.log('API calls are commented out, using mock data');
  console.log('Names mapping:', namesMapping);
  return createMockAnnotatedZip(namesMapping);
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
  
  // Create mock person folders with placeholder images
  const mockPeople = [
    { folder: 'person_1', count: 16 },
    { folder: 'person_2', count: 16 },
    { folder: 'person_3', count: 16 },
  ];
  
  for (const person of mockPeople) {
    for (let i = 1; i <= person.count; i++) {
      // Create a simple colored square as placeholder
      const canvas = document.createElement('canvas');
      canvas.width = 100;
      canvas.height = 100;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Different color for each person
        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1'];
        const personIndex = parseInt(person.folder.split('_')[1]) - 1;
        ctx.fillStyle = colors[personIndex % colors.length];
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
      
      zip.file(`people/${person.folder}/face_${String(i).padStart(3, '0')}.jpg`, blob);
    }
  }
  
  return await zip.generateAsync({ type: 'blob' });
}

/**
 * Create mock annotated ZIP with context
 */
async function createMockAnnotatedZip(namesMapping: Record<string, string>): Promise<Blob> {
  const JSZip = (await import('jszip')).default;
  const zip = new JSZip();
  
  // Create mock memories with context.json
  const mockMemories = ['memory_001', 'memory_002', 'memory_003'];
  
  for (const memory of mockMemories) {
    // Create context.json
    const peopleInMemory = Object.values(namesMapping).filter(() => Math.random() > 0.3);
    const context = {
      memory_id: memory,
      people_identified: peopleInMemory,
      people_count: peopleInMemory.length,
      image_count: Math.floor(Math.random() * 10) + 5,
      description: `A memory featuring ${peopleInMemory.join(', ') || 'unknown people'}.`,
      generated_at: new Date().toISOString(),
    };
    
    zip.file(`memories/${memory}/context.json`, JSON.stringify(context, null, 2));
    
    // Add a placeholder image
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 150;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.fillStyle = '#2C3E50';
      ctx.fillRect(0, 0, 200, 150);
      ctx.fillStyle = 'white';
      ctx.font = '16px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(memory, 100, 75);
    }
    
    const blob = await new Promise<Blob>((resolve) => {
      canvas.toBlob((b) => resolve(b!), 'image/jpeg', 0.8);
    });
    
    zip.file(`memories/${memory}/photo.jpg`, blob);
  }
  
  // Add named people folders
  for (const [personId, name] of Object.entries(namesMapping)) {
    if (name && name.trim()) {
      // Create a few face images for each named person
      for (let i = 1; i <= 5; i++) {
        const canvas = document.createElement('canvas');
        canvas.width = 100;
        canvas.height = 100;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.fillStyle = '#95A5A6';
          ctx.fillRect(0, 0, 100, 100);
          ctx.fillStyle = 'white';
          ctx.font = 'bold 12px Arial';
          ctx.textAlign = 'center';
          ctx.fillText(name, 50, 55);
        }
        
        const blob = await new Promise<Blob>((resolve) => {
          canvas.toBlob((b) => resolve(b!), 'image/jpeg', 0.8);
        });
        
        zip.file(`people/${name}/face_${String(i).padStart(3, '0')}.jpg`, blob);
      }
    }
  }
  
  return await zip.generateAsync({ type: 'blob' });
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
    
    // Extract person folder name (e.g., "people/person_1/face_001.jpg" -> "person_1")
    const parts = filename.split('/');
    if (parts.length >= 2) {
      const folderName = parts[parts.length - 2];
      const imageName = parts[parts.length - 1];
      
      if (folderName.startsWith('person_') && imageName.match(/\.(jpg|jpeg|png)$/i)) {
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
