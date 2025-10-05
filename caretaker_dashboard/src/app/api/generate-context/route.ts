import { NextResponse } from 'next/server';
import path from 'path';
import AdmZip from 'adm-zip';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import os from 'os';

const execAsync = promisify(exec);

interface ContextGenerationResult {
  success: boolean;
  outputPath?: string;
  error?: string;
}

/**
 * This endpoint processes uploaded ZIP files with memories data and a names mapping JSON,
 * extracts all faces (full, not sampled), applies name mappings, generates AI context,
 * and returns a complete annotated dataset.
 */
async function generateContextWithPython(
  inputZipPath: string,
  namesJson: any,
  outputDir: string
): Promise<ContextGenerationResult> {
  try {
    // Python script for full face extraction, naming, and context generation
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
from datetime import datetime
import base64

def generate_context_with_names(zip_path, names_mapping, output_dir):
    """Extract faces, apply names, and generate context for each memory."""
    
    # Create temp directory for extraction
    temp_dir = os.path.join(output_dir, 'temp_extracted')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Extract ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Find memories folder
    memories_dir = None
    for root, dirs, files in os.walk(temp_dir):
        if 'memories' in root.split(os.sep):
            memories_dir = root
            break
    
    if not memories_dir:
        return {'success': False, 'error': 'No memories folder found'}
    
    # Get all memory folders
    memory_folders = []
    for item in os.listdir(memories_dir):
        item_path = os.path.join(memories_dir, item)
        if os.path.isdir(item_path):
            memory_folders.append(item_path)
    
    # Extract all faces from all images with full clustering
    print("Extracting faces from all images...", file=sys.stderr)
    all_faces = []
    face_to_memory = {}  # Track which memory each face came from
    
    for memory_folder in memory_folders:
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        image_files = []
        
        for root, dirs, files in os.walk(memory_folder):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    image_files.append(os.path.join(root, file))
        
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
                    
                    face_id = len(all_faces)
                    all_faces.append({
                        'encoding': encoding,
                        'image': face_img,
                        'source': os.path.basename(img_path),
                        'id': face_id
                    })
                    face_to_memory[face_id] = memory_folder
                    
            except Exception as e:
                print(f"Error processing {img_path}: {e}", file=sys.stderr)
    
    if not all_faces:
        return {'success': False, 'error': 'No faces detected'}
    
    print(f"Found {len(all_faces)} faces total", file=sys.stderr)
    
    # Cluster all faces using DBSCAN
    print("Clustering faces...", file=sys.stderr)
    encodings = np.array([f['encoding'] for f in all_faces])
    clustering = DBSCAN(eps=0.5, min_samples=1, metric='euclidean').fit(encodings)
    
    # Group by cluster
    clusters = {}
    for idx, label in enumerate(clustering.labels_):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(all_faces[idx])
    
    print(f"Created {len(clusters)} face clusters", file=sys.stderr)
    
    # Create face folders with ALL faces (not sampled)
    face_set_id_to_name = {}
    face_set_dirs = {}
    
    for face_set_idx, (cluster_id, faces) in enumerate(clusters.items(), 1):
        face_set_id = f'face_set_{face_set_idx}'
        face_set_dir = os.path.join(output_dir, face_set_id)
        os.makedirs(face_set_dir, exist_ok=True)
        face_set_dirs[face_set_id] = face_set_dir
        
        # Save ALL faces (not sampled)
        for face_idx, face_data in enumerate(faces, 1):
            face_path = os.path.join(face_set_dir, f'{face_idx}.jpg')
            cv2.imwrite(face_path, cv2.cvtColor(face_data['image'], cv2.COLOR_RGB2BGR))
        
        # Check if this face set has a name in the mapping
        face_name = None
        for name, face_set_ids_str in names_mapping.items():
            face_set_ids = [pid.strip() for pid in face_set_ids_str.split(',')]
            if face_set_id in face_set_ids:
                face_name = name
                break
        
        face_set_id_to_name[face_set_id] = face_name or face_set_id
        print(f"Created {face_set_id} with {len(faces)} faces, name: {face_set_id_to_name[face_set_id]}", file=sys.stderr)
    
    # Generate context.json for each memory folder
    print("Generating context for each memory...", file=sys.stderr)
    
    for memory_folder in memory_folders:
        memory_name = os.path.basename(memory_folder)
        
        # Find all faces that belong to this memory
        memory_faces = []
        for face in all_faces:
            if face_to_memory.get(face['id']) == memory_folder:
                # Find which cluster/face set this face belongs to
                face_idx = face['id']
                cluster_label = clustering.labels_[face_idx]
                
                # Find face_set_id for this cluster
                for face_set_idx, (cluster_id, cluster_faces) in enumerate(clusters.items(), 1):
                    if cluster_id == cluster_label:
                        face_set_id = f'face_set_{face_set_idx}'
                        face_name = face_set_id_to_name[face_set_id]
                        if face_name not in memory_faces:
                            memory_faces.append(face_name)
                        break
        
        # Get all images in this memory
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        image_files = []
        for root, dirs, files in os.walk(memory_folder):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    image_files.append(file)
        
        # Generate AI context description
        faces_str = ", ".join(memory_faces) if memory_faces else "unknown faces"
        context_description = f"A memory featuring {faces_str}. "
        context_description += f"This collection contains {len(image_files)} photo(s). "
        
        if memory_faces:
            context_description += f"Faces identified: {', '.join(memory_faces)}."
        
        # Create context.json
        context_data = {
            "memory_id": memory_name,
            "faces_identified": memory_faces,
            "face_count": len(memory_faces),
            "image_count": len(image_files),
            "description": context_description,
            "generated_at": datetime.now().isoformat(),
            "images": image_files
        }
        
        # Save context.json in the memory folder
        context_path = os.path.join(memory_folder, 'context.json')
        with open(context_path, 'w') as f:
            json.dump(context_data, f, indent=2)
        
        print(f"Generated context for {memory_name}: {len(memory_faces)} faces", file=sys.stderr)
    
    return {
        'success': True,
        'face_set_count': len(clusters),
        'memory_count': len(memory_folders),
        'total_faces': len(all_faces)
    }

if __name__ == '__main__':
    zip_path = sys.argv[1]
    names_json_path = sys.argv[2]
    output_dir = sys.argv[3]
    
    # Load names mapping
    with open(names_json_path, 'r') as f:
        names_mapping = json.load(f)
    
    result = generate_context_with_names(zip_path, names_mapping, output_dir)
    print(json.dumps(result))
`;

    // Save Python script to temp file
    const scriptPath = path.join(outputDir, 'generate_context.py');
    await fs.writeFile(scriptPath, pythonScript);

    // Save names JSON to temp file
    const namesJsonPath = path.join(outputDir, 'names.json');
    await fs.writeFile(namesJsonPath, JSON.stringify(namesJson));

    // Execute Python script
    const { stdout, stderr } = await execAsync(
      `python3 "${scriptPath}" "${inputZipPath}" "${namesJsonPath}" "${outputDir}"`,
      { maxBuffer: 50 * 1024 * 1024 } // Increased buffer for larger datasets
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
      error: error.message || 'Failed to generate context'
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
    const dataZipFile = formData.get('data_zip') as File;
    const namesJsonFile = formData.get('names_json') as File;
    
    // Validate required files
    if (!dataZipFile) {
      return NextResponse.json(
        { detail: [{ loc: ['body', 'data_zip'], msg: 'data_zip file is required', type: 'value_error' }] },
        { status: 422 }
      );
    }
    
    if (!namesJsonFile) {
      return NextResponse.json(
        { detail: [{ loc: ['body', 'names_json'], msg: 'names_json file is required', type: 'value_error' }] },
        { status: 422 }
      );
    }
    
    // Create temporary directory
    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'context-generation-'));
    inputZipPath = path.join(tempDir, 'input.zip');
    
    // Save uploaded ZIP file
    const zipArrayBuffer = await dataZipFile.arrayBuffer();
    const zipBuffer = Buffer.from(zipArrayBuffer);
    await fs.writeFile(inputZipPath, zipBuffer);
    
    // Parse names JSON
    const namesJsonText = await namesJsonFile.text();
    let namesJson: any;
    try {
      namesJson = JSON.parse(namesJsonText);
    } catch (parseError) {
      return NextResponse.json(
        { detail: [{ loc: ['body', 'names_json'], msg: 'Invalid JSON format', type: 'value_error' }] },
        { status: 422 }
      );
    }
    
    // Verify memories folder exists in ZIP
    const uploadedZip = new AdmZip(zipBuffer);
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
    
    // Generate context with Python backend
    const result = await generateContextWithPython(inputZipPath, namesJson, tempDir);
    
    if (!result.success) {
      return NextResponse.json(
        { detail: [{ loc: ['server'], msg: result.error || 'Context generation failed', type: 'processing_error' }] },
        { status: 422 }
      );
    }
    
    // Create output ZIP with complete annotated data
    const outputZip = new AdmZip();
    
    // Add all face folders (with full faces, not sampled)
    const entries = await fs.readdir(tempDir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory() && entry.name.startsWith('face_set_')) {
        const faceSetDir = path.join(tempDir, entry.name);
        const faceFiles = await fs.readdir(faceSetDir);
        
        for (const faceFile of faceFiles) {
          const facePath = path.join(faceSetDir, faceFile);
          const faceBuffer = await fs.readFile(facePath);
          outputZip.addFile(`${entry.name}/${faceFile}`, faceBuffer);
        }
      }
    }
    
    // Add memories folder with context.json files
    const tempExtractedDir = path.join(tempDir, 'temp_extracted');
    
    async function addDirectoryToZip(dirPath: string, zipPath: string = '') {
      const items = await fs.readdir(dirPath, { withFileTypes: true });
      
      for (const item of items) {
        const fullPath = path.join(dirPath, item.name);
        const zipItemPath = zipPath ? `${zipPath}/${item.name}` : item.name;
        
        if (item.isDirectory()) {
          await addDirectoryToZip(fullPath, zipItemPath);
        } else {
          const fileBuffer = await fs.readFile(fullPath);
          outputZip.addFile(zipItemPath, fileBuffer);
        }
      }
    }
    
    // Add the entire memories folder structure with context.json files
    if (await fs.access(tempExtractedDir).then(() => true).catch(() => false)) {
      await addDirectoryToZip(tempExtractedDir);
    }
    
    // Generate ZIP buffer
    const outputBuffer = outputZip.toBuffer();
    
    // Cleanup temp directory
    if (tempDir) {
      await fs.rm(tempDir, { recursive: true, force: true });
    }
    
    // Return ZIP file with complete annotated data
    return new NextResponse(outputBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="annotated_memories.zip"',
      },
    });
    
  } catch (error: any) {
    console.error('Error generating context:', error);
    
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
