import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const facesDir = path.join(process.cwd(), 'public', 'faces');
    
    // Check if faces directory exists
    if (!fs.existsSync(facesDir)) {
      return NextResponse.json({ error: 'Faces directory not found' }, { status: 404 });
    }
    
    // Read all subdirectories in faces folder
    const folders = fs.readdirSync(facesDir, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);
    
    // For each folder, get all image files
    const faceSets = folders.map(folder => {
      const folderPath = path.join(facesDir, folder);
      const files = fs.readdirSync(folderPath)
        .filter(file => /\.(jpg|jpeg|png|gif)$/i.test(file))
        .sort(); // Sort alphabetically
      
      return {
        folder,
        images: files
      };
    }).filter(faceSet => faceSet.images.length > 0); // Only include folders with images
    
    return NextResponse.json({ faceSets });
  } catch (error) {
    console.error('Error listing faces:', error);
    return NextResponse.json({ error: 'Failed to list faces' }, { status: 500 });
  }
}
