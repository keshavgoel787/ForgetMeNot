"""
Step 3: Generate context for all memories using AI with people recognition
Uses named people folders to identify who's in each video/image
"""

import sys
import os
from dotenv import load_dotenv
from text_context_per_memory import MemoryContextAnalyzer

def main():
    print("="*70)
    print("STEP 3: CONTEXT GENERATION")
    print("="*70)
    print()
    print("This will:")
    print("  1. Load people reference images (anna, lisa, bob, etc.)")
    print("  2. Analyze all videos and images in memories")
    print("  3. Generate context with people names")
    print("  4. Save to context.json in each memory folder")
    print()
    print("⚠️  WARNING: This will use Gemini API and may take a while!")
    print("⚠️  WARNING: This will cost API credits!")
    print()
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print()
        print("Please create a .env file with your API key:")
        print("GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Configuration
    people_path = "pre_processed/data/people"
    memories_path = "pre_processed/data/memories"
    
    # Ask for confirmation
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        return
    
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
        print("All done! Check context.json in each memory folder for results.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Partial results have been saved to context.json files")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
