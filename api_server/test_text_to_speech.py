"""
Test script for text-to-speech endpoint
"""

import requests
import sys

API_URL = "http://localhost:8000"

def list_voices():
    """List all available voices"""
    print("📋 Available voices:")
    print("="*50)
    
    response = requests.get(f"{API_URL}/voices")
    
    if response.status_code == 200:
        data = response.json()
        voices = data.get("voices", [])
        
        print(f"Found {len(voices)} voice(s):")
        for voice in voices:
            print(f"  - {voice}")
        print()
        return voices
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return []

def generate_speech(name: str, text: str, output_file: str = None):
    """Generate speech using a voice clone"""
    if not output_file:
        output_file = f"{name.lower()}_speech.mp3"
    
    print(f"\n🎤 Generating speech for: {name}")
    print(f"📝 Text: {text}")
    print(f"💾 Output: {output_file}")
    print("="*50)
    
    payload = {
        "text": text,
        "name": name
    }
    
    response = requests.post(
        f"{API_URL}/text-to-speech",
        json=payload
    )
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Success! Saved to: {output_file}")
        print(f"📊 File size: {len(response.content):,} bytes")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        try:
            error = response.json()
            print(f"Details: {error.get('detail', 'Unknown error')}")
        except:
            print(response.text)
        return False

def main():
    print("="*50)
    print("🎙️  Text-to-Speech API Test")
    print("="*50)
    print()
    
    # Step 1: List available voices
    voices = list_voices()
    
    if not voices:
        print("❌ No voices available. Please run upload_voices_to_elevenlabs.py first.")
        sys.exit(1)
    
    # Step 2: Test with first voice
    if len(sys.argv) > 1:
        # Custom text from command line
        test_name = voices[0].capitalize()
        test_text = " ".join(sys.argv[1:])
    else:
        # Default test
        test_name = voices[0].capitalize()
        test_text = "Hi, how are you? This is a test of my voice clone."
    
    generate_speech(test_name, test_text)
    
    # Step 3: Interactive mode
    print("\n" + "="*50)
    print("Interactive Mode")
    print("="*50)
    print("Type 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            # Get name
            print(f"\nAvailable: {', '.join(voices)}")
            name = input("Enter name (or 'quit'): ").strip()
            
            if name.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Get text
            text = input("Enter text to speak: ").strip()
            
            if not text:
                print("❌ Text cannot be empty")
                continue
            
            # Generate
            output = f"{name.lower()}_{len(text)}.mp3"
            generate_speech(name, text, output)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
