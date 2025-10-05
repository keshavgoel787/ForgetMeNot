import os
import json
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import face_recognition
from sklearn.cluster import DBSCAN
from collections import defaultdict
import shutil

class MemoryPeopleExtractor:
    def __init__(self, memories_path: str, output_path: str):
        """Initialize the people extractor"""
        self.memories_path = Path(memories_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Supported file extensions
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        
        # Storage for face data
        self.face_encodings = []
        self.face_images = []
        self.face_metadata = []  # Store source info (file, frame, etc.)
    
    def extract_faces_from_image(self, image_path: str) -> list:
        """Extract all faces from a single image"""
        try:
            print(f"  📸 Processing image: {Path(image_path).name}")
            
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Find all face locations and encodings
            face_locations = face_recognition.face_locations(image, model="hog")
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            faces_data = []
            for idx, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
                top, right, bottom, left = face_location
                
                # Crop face from image
                face_image = image[top:bottom, left:right]
                face_pil = Image.fromarray(face_image)
                
                faces_data.append({
                    'encoding': face_encoding,
                    'image': face_pil,
                    'source_file': str(image_path),
                    'source_type': 'image',
                    'face_index': idx
                })
            
            print(f"     Found {len(faces_data)} face(s)")
            return faces_data
            
        except Exception as e:
            print(f"  ❌ Error processing image: {str(e)}")
            return []
    
    def extract_faces_from_video(self, video_path: str, fps_sample: int = 2) -> list:
        """Extract faces from video by sampling frames"""
        try:
            print(f"  🎥 Processing video: {Path(video_path).name}")
            
            cap = cv2.VideoCapture(video_path)
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(original_fps / fps_sample)
            
            faces_data = []
            frame_count = 0
            processed_frames = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames at specified rate
                if frame_count % frame_interval == 0:
                    # Convert BGR to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Find faces in frame
                    face_locations = face_recognition.face_locations(rgb_frame, model="hog")
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    
                    for idx, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
                        top, right, bottom, left = face_location
                        
                        # Crop face from frame
                        face_image = rgb_frame[top:bottom, left:right]
                        face_pil = Image.fromarray(face_image)
                        
                        faces_data.append({
                            'encoding': face_encoding,
                            'image': face_pil,
                            'source_file': str(video_path),
                            'source_type': 'video',
                            'frame_number': frame_count,
                            'face_index': idx
                        })
                    
                    processed_frames += 1
                
                frame_count += 1
            
            cap.release()
            print(f"     Found {len(faces_data)} face(s) from {processed_frames} frames")
            return faces_data
            
        except Exception as e:
            print(f"  ❌ Error processing video: {str(e)}")
            return []
    
    def process_memory_folder(self, folder_path: str):
        """Extract faces from ONE video per memory folder (TEST MODE)"""
        folder_name = Path(folder_path).name
        print(f"\n🗂️  Processing memory: {folder_name} (TEST MODE - one video only)")
        
        # Find the first video file in the folder
        video_processed = False
        for file_path in sorted(Path(folder_path).iterdir()):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                
                # Only process ONE video per folder
                if ext in self.video_extensions and not video_processed:
                    print(f"  ⚠️  TEST MODE: Processing only first video found")
                    faces = self.extract_faces_from_video(str(file_path))
                    for face_data in faces:
                        self.face_encodings.append(face_data['encoding'])
                        self.face_images.append(face_data['image'])
                        self.face_metadata.append({
                            'memory': folder_name,
                            'source_file': face_data['source_file'],
                            'source_type': face_data['source_type'],
                            'frame_number': face_data.get('frame_number', 0),
                            'face_index': face_data.get('face_index', 0)
                        })
                    video_processed = True
                    break  # Stop after processing one video
        
        if not video_processed:
            print(f"  ⚠️  No video files found in {folder_name}")
    
    def cluster_faces(self, tolerance: float = 0.5):
        """Cluster face encodings into distinct people using DBSCAN"""
        print(f"\n🧩 Clustering {len(self.face_encodings)} faces into people...")
        
        if len(self.face_encodings) == 0:
            print("  ⚠️  No faces found to cluster")
            return
        
        # Convert to numpy array
        encodings_array = np.array(self.face_encodings)
        
        # Use DBSCAN clustering
        # tolerance: lower = stricter matching (more clusters)
        clustering = DBSCAN(metric='euclidean', eps=tolerance, min_samples=2)
        labels = clustering.fit_predict(encodings_array)
        
        # Group faces by cluster
        clustered_faces = defaultdict(list)
        
        for idx, label in enumerate(labels):
            # label = -1 means outlier (single occurrence)
            # We'll keep outliers as separate people too
            person_id = label if label != -1 else f"single_{idx}"
            
            clustered_faces[person_id].append({
                'image': self.face_images[idx],
                'metadata': self.face_metadata[idx],
                'encoding': self.face_encodings[idx]
            })
        
        # Sort clusters by size (most appearances first)
        sorted_clusters = sorted(clustered_faces.items(), 
                                key=lambda x: len(x[1]), 
                                reverse=True)
        
        print(f"  ✅ Found {len(sorted_clusters)} distinct people")
        
        return sorted_clusters
    
    def save_people_folders(self, clustered_faces):
        """Save each person's faces into separate folders"""
        print(f"\n💾 Saving people to folders...")
        
        # Clear existing people folder
        if self.output_path.exists():
            shutil.rmtree(self.output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        for person_idx, (cluster_id, faces) in enumerate(clustered_faces, start=1):
            person_folder = self.output_path / f"person_{person_idx}"
            person_folder.mkdir(exist_ok=True)
            
            print(f"  👤 person_{person_idx}: {len(faces)} images")
            
            # Save metadata about this person
            metadata = {
                'person_id': person_idx,
                'total_appearances': len(faces),
                'memories': list(set(face['metadata']['memory'] for face in faces)),
                'sources': []
            }
            
            # Save each face image
            for face_idx, face_data in enumerate(faces):
                image_filename = f"face_{face_idx:04d}.jpg"
                image_path = person_folder / image_filename
                
                # Save image
                face_data['image'].save(image_path, 'JPEG')
                
                # Add to metadata
                metadata['sources'].append({
                    'image_file': image_filename,
                    'memory': face_data['metadata']['memory'],
                    'source_file': Path(face_data['metadata']['source_file']).name,
                    'source_type': face_data['metadata']['source_type']
                })
            
            # Save metadata JSON
            metadata_path = person_folder / 'metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        print(f"\n✨ Saved {len(clustered_faces)} people to: {self.output_path}")
    
    def process_all_memories(self):
        """Main pipeline: extract faces, cluster, and save (TEST MODE)"""
        print(f"\n🚀 Starting TEST people extraction from: {self.memories_path}")
        print(f"⚠️  TEST MODE: Processing only ONE video per memory folder\n")
        
        # Step 1: Extract faces from ONE video per memory
        memory_folders = [f for f in self.memories_path.iterdir() if f.is_dir()]
        
        for memory_folder in memory_folders:
            self.process_memory_folder(str(memory_folder))
        
        print(f"\n📊 Total faces extracted: {len(self.face_encodings)}")
        
        # Step 2: Cluster faces into people
        clustered_faces = self.cluster_faces(tolerance=0.5)
        
        if clustered_faces:
            # Step 3: Save to person folders
            self.save_people_folders(clustered_faces)
            
            # Step 4: Print summary
            self.print_summary(clustered_faces)
    
    def print_summary(self, clustered_faces):
        """Print summary of detected people"""
        print(f"\n{'='*60}")
        print(f"PEOPLE DETECTION SUMMARY (TEST MODE)")
        print(f"{'='*60}\n")
        
        for person_idx, (cluster_id, faces) in enumerate(clustered_faces, start=1):
            memories = set(face['metadata']['memory'] for face in faces)
            print(f"👤 person_{person_idx}:")
            print(f"   - Total appearances: {len(faces)}")
            print(f"   - Appears in memories: {', '.join(sorted(memories))}")
            print()

def main():
    # Paths
    memories_path = "pre_processed/data/memories"
    people_path = "pre_processed/data/people_test"  # Different output folder for test
    
    print("="*60)
    print("TEST MODE: Memory to People Extraction")
    print("This will process ONLY ONE video per memory folder")
    print("="*60)
    
    # Initialize extractor
    extractor = MemoryPeopleExtractor(memories_path, people_path)
    
    # Process all memories (one video each)
    extractor.process_all_memories()

if __name__ == "__main__":
    main()
