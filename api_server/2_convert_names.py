"""
Step 2: Convert person_X folders to actual names using names.json
Reads names.json and renames/merges person folders accordingly
"""

import sys
import json
from pathlib import Path
from edit_pictures_based_on_json import PeopleFolderEditor

def main():
    print("="*70)
    print("STEP 2: NAME CONVERSION")
    print("="*70)
    print()
    print("This will:")
    print("  1. Read names.json mapping")
    print("  2. Rename person_X folders to actual names")
    print("  3. Merge folders if needed")
    print("  4. Delete unmapped folders")
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
        print()
        print("Or:")
        print(json.dumps({
            "person_1": "anna",
            "person_2": "lisa",
            "person_4": "bob"
        }, indent=2))
        sys.exit(1)
    
    # Preview names.json
    try:
        with open(names_json_path, 'r') as f:
            names_mapping = json.load(f)
        
        print("📋 Current names.json:")
        print(json.dumps(names_mapping, indent=2))
        print()
    except Exception as e:
        print(f"❌ Error reading names.json: {e}")
        sys.exit(1)
    
    # Ask for confirmation
    response = input("Continue with this mapping? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        return
    
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
        print("Next step: Generate context with people names")
        print("Then run: python 3_generate_context.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
