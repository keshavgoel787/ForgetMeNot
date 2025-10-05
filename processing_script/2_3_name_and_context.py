"""
Steps 2 & 3 Combined: Convert names and generate context in one pipeline
1. Convert person_X folders to actual names using names.json
2. Generate AI context with people identification
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from edit_pictures_based_on_json import PeopleFolderEditor
from text_context_per_memory import MemoryContextAnalyzer

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

def step_3_generate_context():
    """Step 3: Generate context with AI"""
    print("\n" + "="*70)
    print("STEP 3: CONTEXT GENERATION")
    print("="*70)
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

def main():
    print("="*70)
    print("COMBINED PIPELINE: NAME CONVERSION + CONTEXT GENERATION")
    print("="*70)
    print()
    print("This will run:")
    print("  Step 2: Convert person_X folders to actual names")
    print("  Step 3: Generate AI context with people identification")
    print()
    
    # Run Step 2
    if not step_2_convert_names():
        print("\n❌ Pipeline failed at Step 2")
        sys.exit(1)
    
    print("\n" + "⏭️ "*35)
    print("Moving to Step 3...")
    print("⏭️ "*35)
    
    # Run Step 3
    if not step_3_generate_context():
        print("\n❌ Pipeline failed at Step 3")
        sys.exit(1)
    
    # Success!
    print("\n" + "🎉"*35)
    print("="*70)
    print("✅ COMPLETE PIPELINE FINISHED!")
    print("="*70)
    print()
    print("All done! Check context.json in each memory folder for results.")
    print("Your people folders are now named: anna/, lisa/, bob/, etc.")

if __name__ == "__main__":
    main()
