import { NextResponse } from 'next/server';
import path from 'path';
import AdmZip from 'adm-zip';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import os from 'os';

const execAsync = promisify(exec);

interface FaceExtractionResult {
  success: boolean;
  outputPath?: string;
  error?: string;
}

/**
 * This endpoint processes uploaded ZIP files containing images/videos,
 * extracts faces, clusters them, and returns a ZIP with organized face folders.
 * 
 * Note: This implementation requires a Python backend with face_recognition library.
 * For production use, consider deploying a separate Python microservice.
 */
async function extractFacesWithPython(inputZipPath: string, outputDir: string): Promise<FaceExtractionResult> {
  try {
    // Python script for face extraction and clustering
    const pythonScript = `
import sys
import os
import zipfile
import cv2
import numpy as np
from pathlib import Path
import json
from sklearn.cluster import DBSCAN
import face_recognition

def extract_faces_from_zip(zip_path, output_dir):
    """Extract faces from images in ZIP file and cluster them."""
    
    # Create temp directory for extraction
    temp_dir = os.path.join(output_dir, 'temp_extracted')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Extract ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Find all images
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    image_files = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                image_files.append(os.path.join(root, file))
    
    # Extract face encodings
    all_faces = []
    for img_path in image_files:
        try:
            image = face_recognition.load_image_file(img_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                # Extract face with padding
                padding = 20
                h, w = image.shape[:2]
                top = max(0, top - padding)
                bottom = min(h, bottom + padding)
                left = max(0, left - padding)
                right = min(w, right + padding)
                
                face_img = image[top:bottom, left:right]
                
                all_faces.append({
                    'encoding': encoding,
                    'image': face_img,
                    'source': os.path.basename(img_path)
                })
        except Exception as e:
            print(f"Error processing {img_path}: {e}", file=sys.stderr)
    
    if not all_faces:
        return {'success': False, 'error': 'No faces detected'}
    
    # Cluster faces using DBSCAN
    encodings = np.array([f['encoding'] for f in all_faces])
    clustering = DBSCAN(eps=0.5, min_samples=1, metric='euclidean').fit(encodings)
    
    # Group by cluster
    clusters = {}
    for idx, label in enumerate(clustering.labels_):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(all_faces[idx])
    
    # Sample and save faces
    person_dirs = []
    for person_idx, (cluster_id, faces) in enumerate(clusters.items(), 1):
        person_dir = os.path.join(output_dir, f'person_{person_idx}')
        os.makedirs(person_dir, exist_ok=True)
        
        # Sample up to 16 faces
        sampled_faces = np.random.choice(faces, min(16, len(faces)), replace=False)
        
        for face_idx, face_data in enumerate(sampled_faces, 1):
            face_path = os.path.join(person_dir, f'{face_idx}.jpg')
            cv2.imwrite(face_path, cv2.cvtColor(face_data['image'], cv2.COLOR_RGB2BGR))
        
        person_dirs.append(person_dir)
    
    return {'success': True, 'person_count': len(clusters)}

if __name__ == '__main__':
    zip_path = sys.argv[1]
    output_dir = sys.argv[2]
    result = extract_faces_from_zip(zip_path, output_dir)
    print(json.dumps(result))
`;

    // Save Python script to temp file
    const scriptPath = path.join(outputDir, 'extract_faces.py');
    await fs.writeFile(scriptPath, pythonScript);

    // Execute Python script
    const { stdout, stderr } = await execAsync(
      `python3 "${scriptPath}" "${inputZipPath}" "${outputDir}"`,
      { maxBuffer: 10 * 1024 * 1024 }
    );

    if (stderr && !stderr.includes('UserWarning')) {
      console.error('Python stderr:', stderr);
    }

    const result = JSON.parse(stdout);
    return { success: result.success, outputPath: outputDir, error: result.error };

  } catch (error: any) {
    console.error('Python execution error:', error);
    return { 
      success: false, 
      error: error.message || 'Failed to execute face extraction'
    };
  }
}

// COMMENTED OUT TO PREVENT ACCIDENTAL API CALLS
/* export async function POST(request: Request) {
  let tempDir: string | null = null;
  let inputZipPath: string | null = null;

  try {
    // Parse multipart form data
    const formData = await request.formData();
    const file = formData.get('data_zip') as File;
    
    if (!file) {
      return NextResponse.json(
        { detail: [{ loc: ['body', 'data_zip'], msg: 'data_zip file is required', type: 'value_error' }] },
        { status: 422 }
      );
    }
    
    // Create temporary directory
    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'face-extraction-'));
    inputZipPath = path.join(tempDir, 'input.zip');
    
    // Save uploaded file
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    await fs.writeFile(inputZipPath, buffer);
    
    // Verify memories folder exists in ZIP
    const uploadedZip = new AdmZip(buffer);
    const zipEntries = uploadedZip.getEntries();
    const memoriesEntries = zipEntries.filter((entry: any) => 
      entry.entryName.includes('memories/') && !entry.isDirectory
    );
    
    if (memoriesEntries.length === 0) {
      return NextResponse.json(
        { detail: [{ loc: ['body', 'data_zip'], msg: 'No memories folder found in ZIP', type: 'value_error' }] },
        { status: 422 }
      );
    }
    
    // Extract faces using Python backend
    const result = await extractFacesWithPython(inputZipPath, tempDir);
    
    if (!result.success) {
      return NextResponse.json(
        { detail: [{ loc: ['server'], msg: result.error || 'Face extraction failed', type: 'processing_error' }] },
        { status: 422 }
      );
    }
    
    // Create output ZIP with extracted faces
    const outputZip = new AdmZip();
    
    // Add all person folders to ZIP
    const entries = await fs.readdir(tempDir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory() && entry.name.startsWith('person_')) {
        const personDir = path.join(tempDir, entry.name);
        const faceFiles = await fs.readdir(personDir);
        
        for (const faceFile of faceFiles) {
          const facePath = path.join(personDir, faceFile);
          const faceBuffer = await fs.readFile(facePath);
          outputZip.addFile(`${entry.name}/${faceFile}`, faceBuffer);
        }
      }
    }
    
    // Generate ZIP buffer
    const outputBuffer = outputZip.toBuffer();
    
    // Cleanup temp directory
    if (tempDir) {
      await fs.rm(tempDir, { recursive: true, force: true });
    }
    
    // Return ZIP file
    return new NextResponse(outputBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="extracted_faces.zip"',
      },
    });
    
  } catch (error: any) {
    console.error('Error processing faces:', error);
    
    // Cleanup on error
    if (tempDir) {
      try {
        await fs.rm(tempDir, { recursive: true, force: true });
      } catch (cleanupError) {
        console.error('Cleanup error:', cleanupError);
      }
    }
    
    return NextResponse.json(
      { detail: [{ loc: ['server'], msg: error.message || 'Internal server error', type: 'server_error' }] },
      { status: 500 }
    );
  }
} */


