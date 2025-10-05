"""
COMPLETE PIPELINE: Names → Context → Audio → Voice Clones
Steps 2, 3, 4, 5 Combined
"""

import sys
import os
import json
import subprocess
import shutil
import requests
import time
from pathlib import Path
from dotenv import load_dotenv
from edit_pictures_based_on_json import PeopleFolderEditor
from text_context_per_memory import MemoryContextAnalyzer

# Load environment variables
load_dotenv()

# ============================================================================
# STEP 2: NAME CONVERSION
# ============================================================================

def step_2_convert_names():
    """Step 2: Convert person folders to actual names"""
    print("="*70)
    print("STEP 2: NAME CONVERSION")
    print("="*70)
    print()
    
    # Configuration
    people_path = "pre_processed/data/people"
    names_json_path = "pre_processed/data/people/names.json"
    
    # Check if names.json exists
    if not Path(names_json_path).exists():
        print("❌ names.json not found!")
        print()
        print("Please create names.json in pre_processed/data/people/")
        print()
        print("Example format:")
        print(json.dumps({
            "anna": "person_1",
            "lisa": "person_2,person_7",
            "bob": "person_4"
        }, indent=2))
        return False
    
    # Preview names.json
    try:
        with open(names_json_path, 'r') as f:
            names_mapping = json.load(f)
        
        print("📋 Current names.json:")
        print(json.dumps(names_mapping, indent=2))
        print()
    except Exception as e:
        print(f"❌ Error reading names.json: {e}")
        return False
    
    # Ask for confirmation
    response = input("Continue with this mapping? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        return False
    
    print("\n🚀 Starting name conversion...\n")
    
    try:
        # Initialize editor
        editor = PeopleFolderEditor(people_path, names_json_path)
        
        # Process the mapping
        editor.process_names_mapping()
        
        print("\n" + "="*70)
        print("✅ STEP 2 COMPLETE!")
        print("="*70)
        print()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# STEP 3: CONTEXT GENERATION
# ============================================================================

def step_3_generate_context():
    """Step 3: Generate context with AI"""
    print("\n" + "="*70)
    print("STEP 3: CONTEXT GENERATION")
    print("="*70)
    print()
    print("⚠️  WARNING: This will use Gemini API and may take a while!")
    print("⚠️  WARNING: This will cost API credits!")
    print()
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print()
        print("Please add to .env file:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    # Configuration
    people_path = "pre_processed/data/people"
    memories_path = "pre_processed/data/memories"
    
    # Ask for confirmation
    response = input("Continue with context generation? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        return False
    
    print("\n🚀 Starting context generation...\n")
    
    try:
        # Initialize analyzer
        print("="*70)
        print("Loading people references...")
        print("="*70)
        analyzer = MemoryContextAnalyzer(api_key, people_path)
        
        # Process all memories
        analyzer.process_all_memories(memories_path)
        
        print("\n" + "="*70)
        print("✅ STEP 3 COMPLETE!")
        print("="*70)
        print()
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Partial results have been saved to context.json files")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# STEP 4: AUDIO EXTRACTION
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
            '-vn',
            '-acodec', 'libmp3lame',
            '-ab', '192k',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        return False

def merge_audio_files(audio_files: list, output_path: str) -> bool:
    """Merge multiple audio files into one"""
    try:
        if not audio_files:
            return False
        
        if len(audio_files) == 1:
            shutil.copy2(audio_files[0], output_path)
            return True
        
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
        concat_file.unlink()
        
        return result.returncode == 0
    except Exception as e:
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
        
        try:
            with open(context_file, 'r') as f:
                context = json.load(f)
        except:
            continue
        
        for key, value in context.items():
            if not key.endswith('_people'):
                continue
            
            people_list = value.lower().strip()
            
            if people_list in ['none', 'unknown', '']:
                continue
            
            people = [p.strip() for p in people_list.split(',')]
            
            if len(people) == 1 and people[0] == person_name.lower():
                video_key = key.replace('_people', '')
                
                video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
                for ext in video_extensions:
                    video_path = memory_folder / f"{video_key}{ext}"
                    if video_path.exists():
                        videos.append(str(video_path))
                        break
    
    return videos

def process_person_audio(person_name: str, person_folder: Path, memories_path: str, temp_dir: Path):
    """Extract and merge audio for one person"""
    videos = find_single_person_videos(memories_path, person_name)
    
    if not videos:
        print(f"  ⚠️  No solo videos found")
        return False
    
    print(f"  📹 Found {len(videos)} solo video(s)")
    
    person_temp = temp_dir / person_name
    person_temp.mkdir(exist_ok=True)
    
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
    
    output_audio = person_folder / f"{person_name}_voice.mp3"
    print(f"  🔗 Merging {len(audio_files)} audio file(s)...")
    
    if merge_audio_files(audio_files, str(output_audio)):
        print(f"  ✅ Saved: {output_audio.name}")
        
        individual_dir = person_folder / "audio_clips"
        individual_dir.mkdir(exist_ok=True)
        
        for audio_file in audio_files:
            dest = individual_dir / Path(audio_file).name
            shutil.copy2(audio_file, dest)
        
        return True
    else:
        return False

def step_4_extract_audio():
    """Step 4: Extract audio from solo videos"""
    print("\n" + "="*70)
    print("STEP 4: AUDIO EXTRACTION")
    print("="*70)
    print()
    
    if not has_ffmpeg():
        print("❌ ERROR: ffmpeg not found!")
        print("Install it with: sudo dnf install ffmpeg")
        return False
    
    memories_path = "pre_processed/data/memories"
    people_path = "pre_processed/data/people"
    temp_dir = Path("temp_audio_extraction")
    
    temp_dir.mkdir(exist_ok=True)
    
    people_dir = Path(people_path)
    person_folders = [f for f in people_dir.iterdir() if f.is_dir()]
    
    extracted_count = 0
    
    for person_folder in sorted(person_folders):
        person_name = person_folder.name
        
        voice_file = person_folder / f"{person_name}_voice.mp3"
        if voice_file.exists():
            print(f"⏭️  {person_name} - Already has voice file")
            continue
        
        print(f"\n📂 Processing: {person_name}")
        
        if process_person_audio(person_name, person_folder, memories_path, temp_dir):
            extracted_count += 1
    
    print(f"\n🧹 Cleaning up temp files...")
    shutil.rmtree(temp_dir)
    
    print()
    print(f"✅ Step 4 Complete: Extracted audio for {extracted_count} people")
    return True

# ============================================================================
# STEP 5: ELEVENLABS UPLOAD
# ============================================================================

def get_elevenlabs_api_key():
    """Get ElevenLabs API key from environment"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ ERROR: ELEVENLABS_API_KEY not found in .env")
        return None
    return api_key

def create_voice_clone(api_key: str, name: str, audio_file_path: str, description: str = None) -> dict:
    """Create a voice clone in ElevenLabs"""
    url = "https://api.elevenlabs.io/v1/voices/add"
    
    headers = {"xi-api-key": api_key}
    files = {"files": (Path(audio_file_path).name, open(audio_file_path, 'rb'), 'audio/mpeg')}
    data = {"name": name}
    
    if description:
        data["description"] = description
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        files["files"][1].close()
        
        if response.status_code == 200:
            result = response.json()
            return {
                "voice_id": result.get("voice_id"),
                "name": name,
                "status": "success"
            }
        else:
            return {"name": name, "status": "failed", "error": response.text}
    except Exception as e:
        return {"name": name, "status": "failed", "error": str(e)}

def list_existing_voices(api_key: str) -> list:
    """List all existing voices in ElevenLabs account"""
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("voices", [])
        return []
    except:
        return []

def step_5_upload_voices():
    """Step 5: Upload voices to ElevenLabs"""
    print("\n" + "="*70)
    print("STEP 5: ELEVENLABS UPLOAD")
    print("="*70)
    print()
    
    api_key = get_elevenlabs_api_key()
    if not api_key:
        print("⚠️  Skipping ElevenLabs upload (no API key)")
        return True  # Don't fail the pipeline
    
    print("✅ API key found")
    
    people_path = Path("pre_processed/data/people")
    
    voice_files = []
    for person_folder in people_path.iterdir():
        if not person_folder.is_dir():
            continue
        
        person_name = person_folder.name
        voice_file = person_folder / f"{person_name}_voice.mp3"
        
        if voice_file.exists():
            voice_files.append({"name": person_name, "path": voice_file})
    
    if not voice_files:
        print("⚠️  No voice files found to upload")
        return True
    
    print(f"📁 Found {len(voice_files)} voice file(s)")
    print("🔍 Checking existing voices in ElevenLabs...")
    
    existing_voices = list_existing_voices(api_key)
    existing_names = {v.get("name"): v.get("voice_id") for v in existing_voices}
    
    uploaded_count = 0
    skipped_count = 0
    
    for i, voice_info in enumerate(voice_files, 1):
        person_name = voice_info["name"]
        voice_path = voice_info["path"]
        elevenlabs_name = f"{person_name}_voice_forgetmenot"
        
        print(f"\n[{i}/{len(voice_files)}] {person_name}")
        
        if elevenlabs_name in existing_names:
            print(f"  ⏭️  Already exists (ID: {existing_names[elevenlabs_name]})")
            skipped_count += 1
            continue
        
        print(f"  📤 Uploading...")
        description = f"Voice clone of {person_name} from ForgetMeNot project"
        
        result = create_voice_clone(api_key, elevenlabs_name, str(voice_path), description)
        
        if result["status"] == "success":
            print(f"  ✅ Created: {elevenlabs_name}")
            print(f"  Voice ID: {result['voice_id']}")
            uploaded_count += 1
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        if i < len(voice_files):
            time.sleep(2)
    
    print()
    print(f"✅ Step 5 Complete: Uploaded {uploaded_count}, Skipped {skipped_count}")
    return True

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    print("="*70)
    print("🚀 COMPLETE PIPELINE: NAMES → CONTEXT → AUDIO → VOICES 🚀")
    print("="*70)
    print()
    print("This will run all steps:")
    print("  Step 2: Convert person_X folders to actual names")
    print("  Step 3: Generate AI context with people identification")
    print("  Step 4: Extract audio from solo videos")
    print("  Step 5: Upload to ElevenLabs for voice cloning")
    print()
    
    response = input("Continue with full pipeline? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        sys.exit(0)
    
    # Step 2: Convert names
    if not step_2_convert_names():
        print("\n❌ Pipeline failed at Step 2")
        sys.exit(1)
    
    print("\n" + "⏭️ "*35)
    print("Moving to Step 3...")
    print("⏭️ "*35)
    
    # Step 3: Generate context
    if not step_3_generate_context():
        print("\n❌ Pipeline failed at Step 3")
        sys.exit(1)
    
    print("\n" + "⏭️ "*35)
    print("Moving to Step 4...")
    print("⏭️ "*35)
    
    # Step 4: Extract audio
    if not step_4_extract_audio():
        print("\n❌ Pipeline failed at Step 4")
        sys.exit(1)
    
    print("\n" + "⏭️ "*35)
    print("Moving to Step 5...")
    print("⏭️ "*35)
    
    # Step 5: Upload voices
    if not step_5_upload_voices():
        print("\n❌ Pipeline failed at Step 5")
        sys.exit(1)
    
    # Success!
    print("\n" + "🎉"*35)
    print("="*70)
    print("✅ COMPLETE PIPELINE FINISHED!")
    print("="*70)
    print()
    print("✅ Names converted (anna/, lisa/, bob/, etc.)")
    print("✅ Context generated (context.json in each memory)")
    print("✅ Audio extracted ({name}_voice.mp3)")
    print("✅ Voices uploaded to ElevenLabs")
    print()
    print("🎤 Your AI voice clones are ready to use!")

if __name__ == "__main__":
    main()
