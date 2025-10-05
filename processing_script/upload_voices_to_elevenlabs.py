"""
Upload voice samples to ElevenLabs to create voice clones
"""

import os
import requests
from pathlib import Path
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_api_key():
    """Get ElevenLabs API key from environment"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ ERROR: ELEVENLABS_API_KEY not found in environment")
        print("Set it with: export ELEVENLABS_API_KEY='your_api_key'")
        print("Or add it to your .env file")
        return None
    return api_key

def create_voice_clone(api_key: str, name: str, audio_file_path: str, description: str = None) -> dict:
    """
    Create a voice clone in ElevenLabs
    
    Args:
        api_key: ElevenLabs API key
        name: Name for the voice
        audio_file_path: Path to the audio file
        description: Optional description
    
    Returns:
        dict with voice_id and name, or None if failed
    """
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
        print(f"  📤 Uploading to ElevenLabs...")
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
            print(f"  ❌ Error: {response.status_code}")
            print(f"  Response: {response.text}")
            return {
                "name": name,
                "status": "failed",
                "error": response.text
            }
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
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
            print(f"⚠️  Could not fetch existing voices: {response.status_code}")
            return []
    except Exception as e:
        print(f"⚠️  Error fetching voices: {e}")
        return []

def main():
    # Paths
    people_path = Path("pre_processed/data/people")
    
    print("="*70)
    print("ELEVENLABS VOICE CLONE UPLOAD")
    print("="*70)
    print()
    print("This will:")
    print("  1. Find all {name}_voice.mp3 files in people folders")
    print("  2. Upload them to ElevenLabs to create voice clones")
    print("  3. Name them as {name}_voice_forgetmenot")
    print()
    
    # Check for API key
    api_key = get_api_key()
    if not api_key:
        return
    
    print("✅ API key found")
    print()
    
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
        print(f"Looking in: {people_path}")
        return
    
    print(f"📁 Found {len(voice_files)} voice file(s):")
    for vf in voice_files:
        print(f"  - {vf['name']}")
    print()
    
    # Check existing voices
    print("🔍 Checking existing voices in ElevenLabs...")
    existing_voices = list_existing_voices(api_key)
    existing_names = {v.get("name"): v.get("voice_id") for v in existing_voices}
    
    if existing_voices:
        print(f"  Found {len(existing_voices)} existing voice(s)")
    print()
    
    response = input("Continue with upload? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        return
    
    print()
    
    # Upload each voice
    results = []
    
    for i, voice_info in enumerate(voice_files, 1):
        person_name = voice_info["name"]
        voice_path = voice_info["path"]
        elevenlabs_name = f"{person_name}_voice_forgetmenot"
        
        print(f"{'='*60}")
        print(f"[{i}/{len(voice_files)}] Processing: {person_name}")
        print(f"{'='*60}")
        
        # Check if already exists
        if elevenlabs_name in existing_names:
            print(f"  ⚠️  Voice '{elevenlabs_name}' already exists in ElevenLabs")
            print(f"  Voice ID: {existing_names[elevenlabs_name]}")
            print(f"  ⏭️  Skipping...")
            results.append({
                "name": person_name,
                "elevenlabs_name": elevenlabs_name,
                "status": "skipped",
                "voice_id": existing_names[elevenlabs_name]
            })
            print()
            continue
        
        # Create description
        description = f"Voice clone of {person_name} from ForgetMeNot project"
        
        # Upload
        result = create_voice_clone(
            api_key=api_key,
            name=elevenlabs_name,
            audio_file_path=str(voice_path),
            description=description
        )
        
        if result["status"] == "success":
            print(f"  ✅ Created voice: {elevenlabs_name}")
            print(f"  Voice ID: {result['voice_id']}")
        else:
            print(f"  ❌ Failed to create voice: {elevenlabs_name}")
        
        results.append({
            "name": person_name,
            "elevenlabs_name": elevenlabs_name,
            **result
        })
        
        print()
        
        # Wait a bit between uploads to avoid rate limits
        if i < len(voice_files):
            time.sleep(2)
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print()
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    skipped = [r for r in results if r["status"] == "skipped"]
    
    print(f"✅ Successfully created: {len(successful)}")
    for r in successful:
        print(f"   - {r['elevenlabs_name']} (ID: {r['voice_id']})")
    print()
    
    if skipped:
        print(f"⏭️  Skipped (already exists): {len(skipped)}")
        for r in skipped:
            print(f"   - {r['elevenlabs_name']}")
        print()
    
    if failed:
        print(f"❌ Failed: {len(failed)}")
        for r in failed:
            print(f"   - {r['name']}: {r.get('error', 'Unknown error')}")
        print()
    
    print("="*70)
    print("✅ COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()
