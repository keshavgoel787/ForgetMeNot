"""
Test script for lip-sync video generation endpoint
"""

import requests
import sys
import os

API_URL = "http://localhost:8000"

def test_lipsync(image_path: str, audio_path: str):
    """
    Test the lip-sync endpoint with local files
    
    Args:
        image_path: Path to image file (jpg, png)
        audio_path: Path to audio file (mp3, wav)
    """
    
    # Check if files exist
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return False
    
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        return False
    
    print("🎬 Testing Lip-Sync Endpoint")
    print("=" * 60)
    print(f"📸 Image: {image_path}")
    print(f"🎵 Audio: {audio_path}")
    print("=" * 60)
    
    try:
        # Prepare files for upload
        files = {
            'image': open(image_path, 'rb'),
            'audio': open(audio_path, 'rb')
        }
        
        print("\n⏳ Uploading files and generating video...")
        print("   (This may take 30-120 seconds)")
        
        # Make request
        response = requests.post(
            f"{API_URL}/lipsync",
            files=files,
            timeout=180  # 3 minute timeout
        )
        
        # Close file handles
        for f in files.values():
            f.close()
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Video generated!")
            print("=" * 60)
            print(f"\n📹 Video URL: {result['video_url']}")
            print(f"🌐 View online: {result['gooey_url']}")
            print(f"🆔 Run ID: {result['run_id']}")
            
            # Download the video
            print("\n⏬ Downloading video...")
            video_response = requests.get(result['video_url'])
            
            output_filename = "lipsync_output.mp4"
            with open(output_filename, 'wb') as f:
                f.write(video_response.content)
            
            print(f"✅ Video saved to: {output_filename}")
            print(f"📊 File size: {len(video_response.content):,} bytes")
            
            return True
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            try:
                error = response.json()
                print(f"Details: {error.get('detail', 'Unknown error')}")
            except:
                print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out!")
        print("   The video generation is taking too long.")
        print("   Try with:")
        print("   - Shorter audio file")
        print("   - Smaller image")
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {API_URL}")
        print("   Is the server running?")
        print("   Start it with: python main.py")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def test_with_text_to_speech(image_path: str, text: str, voice_name: str):
    """
    Complete workflow: text → speech → lip-sync video
    
    Args:
        image_path: Path to image file
        text: Text to speak
        voice_name: Name of voice to use
    """
    
    print("🎭 Complete Workflow Test")
    print("=" * 60)
    print(f"📸 Image: {image_path}")
    print(f"💬 Text: {text}")
    print(f"🎤 Voice: {voice_name}")
    print("=" * 60)
    
    # Step 1: Generate speech
    print("\n⏳ Step 1: Generating speech...")
    
    tts_response = requests.post(
        f"{API_URL}/text-to-speech",
        json={
            'text': text,
            'name': voice_name
        }
    )
    
    if tts_response.status_code != 200:
        print(f"❌ Text-to-speech failed: {tts_response.status_code}")
        print(tts_response.json())
        return False
    
    # Save the audio
    audio_path = f"{voice_name}_generated.mp3"
    with open(audio_path, 'wb') as f:
        f.write(tts_response.content)
    
    print(f"✅ Speech generated: {audio_path}")
    
    # Step 2: Create lip-sync video
    print("\n⏳ Step 2: Creating lip-sync video...")
    
    return test_lipsync(image_path, audio_path)

def main():
    """Main test function"""
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Test with files:")
        print("    python test_lipsync.py <image_path> <audio_path>")
        print("")
        print("  Test with text-to-speech:")
        print("    python test_lipsync.py <image_path> --text <text> --voice <name>")
        print("")
        print("Examples:")
        print("  python test_lipsync.py photo.jpg speech.mp3")
        print("  python test_lipsync.py photo.jpg --text 'Hello world' --voice Hannah")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Check if using text-to-speech workflow
    if len(sys.argv) > 2 and sys.argv[2] == '--text':
        if len(sys.argv) < 6 or sys.argv[4] != '--voice':
            print("❌ Invalid arguments for text-to-speech workflow")
            print("Usage: python test_lipsync.py <image> --text <text> --voice <name>")
            sys.exit(1)
        
        text = sys.argv[3]
        voice_name = sys.argv[5]
        
        success = test_with_text_to_speech(image_path, text, voice_name)
    else:
        # Regular workflow with audio file
        audio_path = sys.argv[2]
        success = test_lipsync(image_path, audio_path)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Tests failed")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
