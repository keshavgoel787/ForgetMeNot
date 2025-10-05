"""
Test script for text-to-sound generation endpoint
"""

import requests
import sys

API_URL = "http://localhost:8000"

def test_text_to_sound(text: str, duration: float = None, prompt_influence: float = 0.3):
    """
    Test the text-to-sound endpoint
    
    Args:
        text: Description of sound/music to generate
        duration: Optional duration in seconds (0.5-30)
        prompt_influence: How closely to follow prompt (0-1)
    """
    
    print("🎵 Testing Text-to-Sound Endpoint")
    print("=" * 60)
    print(f"📝 Prompt: {text}")
    if duration:
        print(f"⏱️  Duration: {duration}s")
    print(f"🎯 Prompt Influence: {prompt_influence}")
    print("=" * 60)
    
    try:
        # Prepare request
        payload = {
            'text': text,
            'prompt_influence': prompt_influence
        }
        
        if duration is not None:
            payload['duration_seconds'] = duration
        
        print("\n⏳ Generating audio...")
        print("   (This may take 10-45 seconds)")
        
        # Make request
        response = requests.post(
            f"{API_URL}/text-to-sound",
            json=payload,
            timeout=60
        )
        
        # Check response
        if response.status_code == 200:
            # Save the audio
            filename = f"generated_sound_{text[:30].replace(' ', '_')}.mp3"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Audio generated!")
            print("=" * 60)
            print(f"\n📁 Saved to: {filename}")
            print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print(f"\n🎧 Play it with:")
            print(f"   ffplay {filename}")
            print(f"   or any MP3 player")
            
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
        print("   The audio generation is taking too long.")
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {API_URL}")
        print("   Is the server running?")
        print("   Start it with: python main.py")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def test_multiple_sounds():
    """Generate a variety of sound effects and music"""
    
    print("\n" + "=" * 60)
    print("🎼 RUNNING MULTIPLE SOUND TESTS")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Epic Music",
            "text": "Epic cinematic orchestral music with drums and strings",
            "duration": 10,
            "prompt_influence": 0.6
        },
        {
            "name": "Rain Sound",
            "text": "Gentle rain falling on leaves",
            "duration": 5,
            "prompt_influence": 0.4
        },
        {
            "name": "Glass Breaking",
            "text": "Glass shattering on concrete",
            "duration": None,  # Auto duration
            "prompt_influence": 0.7
        },
        {
            "name": "EDM Music",
            "text": "Upbeat electronic dance music with heavy bass",
            "duration": 15,
            "prompt_influence": 0.5
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n\n{'='*60}")
        print(f"Test {i}/{len(test_cases)}: {test['name']}")
        print(f"{'='*60}")
        
        success = test_text_to_sound(
            text=test['text'],
            duration=test['duration'],
            prompt_influence=test['prompt_influence']
        )
        
        results.append({
            'name': test['name'],
            'success': success
        })
        
        if i < len(test_cases):
            print("\n⏸️  Waiting 2 seconds before next test...")
            import time
            time.sleep(2)
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} - {result['name']}")
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    return all(r['success'] for r in results)

def main():
    """Main test function"""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single test:")
        print("    python test_text_to_sound.py '<text>' [duration] [prompt_influence]")
        print("")
        print("  Multiple tests:")
        print("    python test_text_to_sound.py --test-all")
        print("")
        print("Examples:")
        print("  python test_text_to_sound.py 'Epic orchestral music'")
        print("  python test_text_to_sound.py 'Thunder sound' 5 0.8")
        print("  python test_text_to_sound.py --test-all")
        sys.exit(1)
    
    if sys.argv[1] == '--test-all':
        success = test_multiple_sounds()
    else:
        text = sys.argv[1]
        duration = float(sys.argv[2]) if len(sys.argv) > 2 else None
        prompt_influence = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
        
        success = test_text_to_sound(text, duration, prompt_influence)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
