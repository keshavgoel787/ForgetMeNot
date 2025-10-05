"""
Create people_2 folder with 16 randomly sampled faces from each person in people folder
"""

import random
import shutil
from pathlib import Path

def sample_people_faces(input_dir: str = "pre_processed/data/people", 
                       output_dir: str = "pre_processed/data/people_2",
                       sample_size: int = 16):
    """
    Create a new people folder with randomly sampled faces
    
    Args:
        input_dir: Source people folder
        output_dir: Destination folder for sampled faces
        sample_size: Number of faces to sample per person (default 16)
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print(f"SAMPLING PEOPLE FACES: {sample_size} per person")
    print("="*70)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print()
    
    # Process each person folder
    person_folders = [f for f in input_path.iterdir() if f.is_dir() and f.name.startswith('person_')]
    
    total_processed = 0
    total_sampled = 0
    
    for person_folder in sorted(person_folders):
        person_name = person_folder.name
        
        # Get all face images
        face_files = list(person_folder.glob("face_*.jpg"))
        
        if not face_files:
            print(f"⚠️  {person_name}: No face images found, skipping")
            continue
        
        # Sample faces
        if len(face_files) <= sample_size:
            # Take all if less than sample size
            sampled_faces = face_files
        else:
            # Randomly sample
            sampled_faces = random.sample(face_files, sample_size)
        
        # Create output folder for this person
        output_person_folder = output_path / person_name
        output_person_folder.mkdir(exist_ok=True)
        
        # Copy sampled faces
        for face_file in sampled_faces:
            dest_file = output_person_folder / face_file.name
            shutil.copy2(face_file, dest_file)
        
        # Copy metadata if exists
        metadata_file = person_folder / "metadata.json"
        if metadata_file.exists():
            dest_metadata = output_person_folder / "metadata.json"
            shutil.copy2(metadata_file, dest_metadata)
        
        total_processed += 1
        total_sampled += len(sampled_faces)
        
        print(f"✅ {person_name}: {len(sampled_faces)}/{len(face_files)} faces sampled")
    
    print()
    print("="*70)
    print(f"✅ COMPLETE!")
    print("="*70)
    print(f"Processed: {total_processed} people")
    print(f"Total faces sampled: {total_sampled}")
    print(f"Output: {output_path}")

def main():
    print("\n🎯 Creating 'people_2' with 16 random samples per person\n")
    sample_people_faces()

if __name__ == "__main__":
    main()
