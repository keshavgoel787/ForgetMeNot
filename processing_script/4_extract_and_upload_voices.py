"""
Combined pipeline: Extract audio from videos + Upload to ElevenLabs
"""

import json
import subprocess
import shutil
import os
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# PART 1: AUDIO EXTRACTION
# ============================================================================

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
    """Find all videos where only this person appears"""
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
            
            # Check if ONLY this person appears
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
    # Find videos with only this person
    videos = find_single_person_videos(memories_path, person_name)
    
    if not videos:
        print(f"  ⚠️  No solo videos found")
        return False
    
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
    
    if not audio_files:
        print(f"  ❌ No audio extracted")
        return False
    
    # Merge all audio files
    output_audio = person_folder / f"{person_name}_voice.mp3"
    print(f"  🔗 Merging {len(audio_files)} audio file(s)...")
    
    if merge_audio_files(audio_files, str(output_audio)):
        print(f"  ✅ Saved: {output_audio.name}")
        
        # Also save individual audio files
        individual_dir = person_folder / "audio_clips"
        individual_dir.mkdir(exist_ok=True)
        
        for audio_file in audio_files:
            dest = individual_dir / Path(audio_file).name
            shutil.copy2(audio_file, dest)
        
        return True
    else:
        return False

def step_1_extract_audio():
    """Step 1: Extract and merge audio from solo videos"""
    print("\n" + "="*70)
    print("STEP 1: AUDIO EXTRACTION")
    print("="*70)
    print()
    
    # Paths
    memories_path = "pre_processed/data/memories"
    people_path = "pre_processed/data/people"
    temp_dir = Path("temp_audio_extraction")
    
    # Check for ffmpeg
    if not has_ffmpeg():
        print("❌ ERROR: ffmpeg not found!")
        print("Install it with: sudo dnf install ffmpeg")
        return False
    
    # Create temp directory
    temp_dir.mkdir(exist_ok=True)
    
    # Process each person folder
    people_dir = Path(people_path)
    person_folders = [f for f in people_dir.iterdir() if f.is_dir()]
    
    extracted_count = 0
    
    for person_folder in sorted(person_folders):
        person_name = person_folder.name
        
        # Skip if already has voice file
        voice_file = person_folder / f"{person_name}_voice.mp3"
        if voice_file.exists():
            print(f"⏭️  {person_name} - Already has voice file")
            continue
        
        print(f"\n📂 Processing: {person_name}")
        
        if process_person_audio(person_name, person_folder, memories_path, temp_dir):
            extracted_count += 1
    
    # Cleanup temp directory
    print(f"\n🧹 Cleaning up temp files...")
    shutil.rmtree(temp_dir)
    
    print()
    print(f"✅ Step 1 Complete: Extracted audio for {extracted_count} people")
    return True

# ============================================================================
# PART 2: ELEVENLABS UPLOAD
# ============================================================================

def get_api_key():
    """Get ElevenLabs API key from environment"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ ERROR: ELEVENLABS_API_KEY not found in environment")
        print("Add it to your .env file: ELEVENLABS_API_KEY=your_key")
        return None
    return api_key

def create_voice_clone(api_key: str, name: str, audio_file_path: str, description: str = None) -> dict:
    """Create a voice clone in ElevenLabs"""
    url = "https://api.elevenlabs.io/v1/voices/add"
    
    headers = {
        "xi-api-key": api_key
    }
    
    # Prepare the files
    files = {
        "files": (Path(audio_file_path).name, open(audio_file_path, 'rb'), 'audio/mpeg')
    }
    
    # Prepare the data
    data = {
        "name": name,
    }
    
    if description:
        data["description"] = description
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        
        # Close the file
        files["files"][1].close()
        
        if response.status_code == 200:
            result = response.json()
            return {
                "voice_id": result.get("voice_id"),
                "name": name,
                "status": "success"
            }
        else:
            return {
                "name": name,
                "status": "failed",
                "error": response.text
            }
    except Exception as e:
        return {
            "name": name,
            "status": "failed",
            "error": str(e)
        }

def list_existing_voices(api_key: str) -> list:
    """List all existing voices in ElevenLabs account"""
    url = "https://api.elevenlabs.io/v1/voices"
    
    headers = {
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result.get("voices", [])
        else:
            return []
    except Exception as e:
        return []

def step_2_upload_voices():
    """Step 2: Upload voices to ElevenLabs"""
    print("\n" + "="*70)
    print("STEP 2: ELEVENLABS UPLOAD")
    print("="*70)
    print()
    
    # Check for API key
    api_key = get_api_key()
    if not api_key:
        return False
    
    print("✅ API key found")
    
    # Paths
    people_path = Path("pre_processed/data/people")
    
    # Find all voice files
    voice_files = []
    for person_folder in people_path.iterdir():
        if not person_folder.is_dir():
            continue
        
        person_name = person_folder.name
        voice_file = person_folder / f"{person_name}_voice.mp3"
        
        if voice_file.exists():
            voice_files.append({
                "name": person_name,
                "path": voice_file
            })
    
    if not voice_files:
        print("❌ No voice files found!")
        return False
    
    print(f"📁 Found {len(voice_files)} voice file(s)")
    
    # Check existing voices
    print("🔍 Checking existing voices in ElevenLabs...")
    existing_voices = list_existing_voices(api_key)
    existing_names = {v.get("name"): v.get("voice_id") for v in existing_voices}
    
    # Upload each voice
    results = []
    uploaded_count = 0
    skipped_count = 0
    
    for i, voice_info in enumerate(voice_files, 1):
        person_name = voice_info["name"]
        voice_path = voice_info["path"]
        elevenlabs_name = f"{person_name}_voice_forgetmenot"
        
        print(f"\n[{i}/{len(voice_files)}] {person_name}")
        
        # Check if already exists
        if elevenlabs_name in existing_names:
            print(f"  ⏭️  Already exists (ID: {existing_names[elevenlabs_name]})")
            skipped_count += 1
            continue
        
        # Upload
        print(f"  📤 Uploading...")
        description = f"Voice clone of {person_name} from ForgetMeNot project"
        
        result = create_voice_clone(
            api_key=api_key,
            name=elevenlabs_name,
            audio_file_path=str(voice_path),
            description=description
        )
        
        if result["status"] == "success":
            print(f"  ✅ Created: {elevenlabs_name}")
            print(f"  Voice ID: {result['voice_id']}")
            uploaded_count += 1
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Wait between uploads
        if i < len(voice_files):
            time.sleep(2)
    
    print()
    print(f"✅ Step 2 Complete: Uploaded {uploaded_count}, Skipped {skipped_count}")
    return True

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    print("="*70)
    print("COMBINED PIPELINE: AUDIO EXTRACTION + ELEVENLABS UPLOAD")
    print("="*70)
    print()
    print("This will:")
    print("  Step 1: Extract audio from solo videos")
    print("  Step 2: Upload to ElevenLabs for voice cloning")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        return
    
    # Step 1: Extract audio
    if not step_1_extract_audio():
        print("\n❌ Pipeline failed at Step 1")
        return
    
    print("\n" + "⏭️ "*35)
    print("Moving to Step 2...")
    print("⏭️ "*35)
    
    # Step 2: Upload to ElevenLabs
    if not step_2_upload_voices():
        print("\n❌ Pipeline failed at Step 2")
        return
    
    # Final summary
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE!")
    print("="*70)
    print()
    print("All voices extracted and uploaded to ElevenLabs!")
    print("Check your ElevenLabs dashboard to use the voice clones.")

if __name__ == "__main__":
    main()
