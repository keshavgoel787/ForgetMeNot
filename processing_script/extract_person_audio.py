"""
Extract and merge audio from videos where only one person appears
"""

import json
import subprocess
from pathlib import Path
import shutil

def has_ffmpeg():
    """Check if ffmpeg is installed"""
    return shutil.which('ffmpeg') is not None

def extract_audio(video_path: str, output_path: str) -> bool:
    """Extract audio from video using ffmpeg"""
    try:
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',  # MP3 codec
            '-ab', '192k',  # Bitrate
            '-y',  # Overwrite output
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"  ❌ Error extracting audio: {e}")
        return False

def merge_audio_files(audio_files: list, output_path: str) -> bool:
    """Merge multiple audio files into one using ffmpeg concat"""
    try:
        if not audio_files:
            return False
        
        if len(audio_files) == 1:
            # Just copy if only one file
            shutil.copy2(audio_files[0], output_path)
            return True
        
        # Create a temporary file list for ffmpeg concat
        concat_file = Path(output_path).parent / "concat_list.txt"
        
        with open(concat_file, 'w') as f:
            for audio_file in audio_files:
                f.write(f"file '{Path(audio_file).absolute()}'\n")
        
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up concat file
        concat_file.unlink()
        
        return result.returncode == 0
    except Exception as e:
        print(f"  ❌ Error merging audio: {e}")
        return False

def find_single_person_videos(memories_path: str, person_name: str) -> list:
    """
    Find all videos where only this person appears
    Returns list of video paths
    """
    videos = []
    memories_dir = Path(memories_path)
    
    for memory_folder in memories_dir.iterdir():
        if not memory_folder.is_dir():
            continue
        
        context_file = memory_folder / "context.json"
        if not context_file.exists():
            continue
        
        # Load context
        try:
            with open(context_file, 'r') as f:
                context = json.load(f)
        except Exception as e:
            print(f"  ⚠️  Could not load {context_file}: {e}")
            continue
        
        # Check each video entry
        for key, value in context.items():
            if not key.endswith('_people'):
                continue
            
            # Check if only this person appears
            people_list = value.lower().strip()
            
            # Skip if no people or unknown
            if people_list in ['none', 'unknown', '']:
                continue
            
            # Parse people list
            people = [p.strip() for p in people_list.split(',')]
            
            # Check if ONLY this person appears (and no one else)
            if len(people) == 1 and people[0] == person_name.lower():
                # Get video filename
                video_key = key.replace('_people', '')
                
                # Find the actual video file
                video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
                for ext in video_extensions:
                    video_path = memory_folder / f"{video_key}{ext}"
                    if video_path.exists():
                        videos.append(str(video_path))
                        break
    
    return videos

def process_person_audio(person_name: str, person_folder: Path, memories_path: str, temp_dir: Path):
    """Extract and merge audio for one person"""
    print(f"\n{'='*60}")
    print(f"Processing: {person_name}")
    print(f"{'='*60}")
    
    # Find videos with only this person
    videos = find_single_person_videos(memories_path, person_name)
    
    if not videos:
        print(f"  ⚠️  No solo videos found for {person_name}")
        return
    
    print(f"  📹 Found {len(videos)} solo video(s)")
    
    # Create temp directory for this person
    person_temp = temp_dir / person_name
    person_temp.mkdir(exist_ok=True)
    
    # Extract audio from each video
    audio_files = []
    for i, video_path in enumerate(videos):
        video_name = Path(video_path).stem
        audio_path = person_temp / f"audio_{i:03d}_{video_name}.mp3"
        
        print(f"  🎵 Extracting audio {i+1}/{len(videos)}: {video_name}")
        
        if extract_audio(video_path, str(audio_path)):
            audio_files.append(str(audio_path))
        else:
            print(f"    ⚠️  Failed to extract audio from {video_name}")
    
    if not audio_files:
        print(f"  ❌ No audio extracted for {person_name}")
        return
    
    # Merge all audio files
    output_audio = person_folder / f"{person_name}_voice.mp3"
    print(f"  🔗 Merging {len(audio_files)} audio file(s)...")
    
    if merge_audio_files(audio_files, str(output_audio)):
        print(f"  ✅ Saved merged audio: {output_audio.name}")
        
        # Also save individual audio files
        individual_dir = person_folder / "audio_clips"
        individual_dir.mkdir(exist_ok=True)
        
        for audio_file in audio_files:
            dest = individual_dir / Path(audio_file).name
            shutil.copy2(audio_file, dest)
        
        print(f"  📁 Saved {len(audio_files)} individual clip(s) to: audio_clips/")
    else:
        print(f"  ❌ Failed to merge audio for {person_name}")

def main():
    # Paths
    memories_path = "pre_processed/data/memories"
    people_path = "pre_processed/data/people"
    temp_dir = Path("temp_audio_extraction")
    
    # Check for ffmpeg
    if not has_ffmpeg():
        print("❌ ERROR: ffmpeg not found!")
        print("Install it with: sudo apt install ffmpeg")
        return
    
    print("="*70)
    print("AUDIO EXTRACTION FROM SOLO VIDEOS")
    print("="*70)
    print()
    print("This will:")
    print("  1. Find videos where only one person appears")
    print("  2. Extract audio from those videos")
    print("  3. Merge all audio clips per person")
    print("  4. Save to person folder as {name}_voice.mp3")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        return
    
    print()
    
    # Create temp directory
    temp_dir.mkdir(exist_ok=True)
    
    # Process each person folder
    people_dir = Path(people_path)
    person_folders = [f for f in people_dir.iterdir() if f.is_dir()]
    
    total_processed = 0
    
    for person_folder in sorted(person_folders):
        person_name = person_folder.name
        
        # Skip if already has voice file
        voice_file = person_folder / f"{person_name}_voice.mp3"
        if voice_file.exists():
            print(f"\n⏭️  Skipping {person_name} (already has voice file)")
            continue
        
        process_person_audio(person_name, person_folder, memories_path, temp_dir)
        total_processed += 1
    
    # Cleanup temp directory
    print(f"\n🧹 Cleaning up temp files...")
    shutil.rmtree(temp_dir)
    
    print()
    print("="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print(f"Processed: {total_processed} people")
    print(f"Output: {people_path}/{{person_name}}_voice.mp3")

if __name__ == "__main__":
    main()
