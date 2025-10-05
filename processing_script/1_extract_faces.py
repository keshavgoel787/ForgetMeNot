"""
Step 1: Extract faces from all memory videos/images and cluster them into person_1, person_2, etc.
Creates folders in pre_processed/data/people/
"""

import sys
from memory_to_people import MemoryPeopleExtractor

def main():
    print("="*70)
    print("STEP 1: FACE EXTRACTION & CLUSTERING")
    print("="*70)
    print()
    print("This will:")
    print("  1. Extract faces from all videos and images in memories")
    print("  2. Cluster similar faces together")
    print("  3. Create person_1, person_2, person_3... folders")
    print()
    
    # Configuration
    memories_path = "pre_processed/data/memories"
    people_output_path = "pre_processed/data/people"
    
    # Ask for confirmation
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled")
        return
    
    print("\n🚀 Starting face extraction...\n")
    
    try:
        # Initialize extractor
        extractor = MemoryPeopleExtractor(memories_path, people_output_path)
        
        # Process all memories
        extractor.process_all_memories()
        
        print("\n" + "="*70)
        print("✅ STEP 1 COMPLETE!")
        print("="*70)
        print()
        print("Next step: Edit names.json to map person_X folders to actual names")
        print("Then run: python 2_convert_names.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
