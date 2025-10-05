import os
import json
import shutil
from pathlib import Path
from collections import defaultdict

class PeopleFolderEditor:
    def __init__(self, people_path: str, names_json_path: str):
        """Initialize the folder editor"""
        self.people_path = Path(people_path)
        self.names_json_path = Path(names_json_path)
        
        if not self.people_path.exists():
            raise FileNotFoundError(f"People folder not found: {self.people_path}")
        
        if not self.names_json_path.exists():
            raise FileNotFoundError(f"names.json not found: {self.names_json_path}")
    
    def load_names_mapping(self):
        """Load the names.json file"""
        with open(self.names_json_path, 'r') as f:
            content = f.read().strip()
            if not content:
                print("⚠️  names.json is empty!")
                return {}
            return json.loads(content)
    
    def get_all_person_folders(self):
        """Get all person_X folders in the people directory"""
        return [f for f in self.people_path.iterdir() 
                if f.is_dir() and f.name.startswith('person_')]
    
    def merge_folders(self, source_folders: list, target_name: str):
        """Merge multiple person folders into one named folder"""
        target_folder = self.people_path / target_name
        target_folder.mkdir(exist_ok=True)
        
        print(f"  🔀 Merging {len(source_folders)} folders into '{target_name}'")
        
        # Collect all face images and metadata from source folders
        all_sources = []
        face_counter = 0
        
        for source_folder in source_folders:
            if not source_folder.exists():
                print(f"    ⚠️  Folder not found: {source_folder.name}")
                continue
            
            print(f"    📂 Merging from: {source_folder.name}")
            
            # Copy all face images
            for face_file in source_folder.glob('face_*.jpg'):
                new_filename = f"face_{face_counter:04d}.jpg"
                shutil.copy2(face_file, target_folder / new_filename)
                face_counter += 1
            
            # Read metadata if it exists
            metadata_file = source_folder / 'metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    all_sources.extend(metadata.get('sources', []))
        
        # Create merged metadata
        if all_sources:
            merged_metadata = {
                'name': target_name,
                'total_appearances': face_counter,
                'merged_from': [f.name for f in source_folders if f.exists()],
                'sources': all_sources
            }
            
            with open(target_folder / 'metadata.json', 'w') as f:
                json.dump(merged_metadata, f, indent=2)
        
        print(f"    ✅ Merged {face_counter} face images")
        
        # Remove source folders
        for source_folder in source_folders:
            if source_folder.exists():
                shutil.rmtree(source_folder)
                print(f"    🗑️  Deleted: {source_folder.name}")
    
    def rename_folder(self, source_folder: Path, new_name: str):
        """Rename a person folder to a new name"""
        target_folder = self.people_path / new_name
        
        if target_folder.exists():
            print(f"  ⚠️  Folder '{new_name}' already exists, skipping rename")
            return
        
        print(f"  📝 Renaming '{source_folder.name}' → '{new_name}'")
        
        # Rename the folder
        shutil.move(str(source_folder), str(target_folder))
        
        # Update metadata with the name
        metadata_file = target_folder / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            metadata['name'] = new_name
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        print(f"    ✅ Renamed successfully")
    
    def delete_folder(self, folder: Path):
        """Delete a person folder"""
        print(f"  🗑️  Deleting folder: {folder.name}")
        shutil.rmtree(folder)
        print(f"    ✅ Deleted successfully")
    
    def process_names_mapping(self):
        """Main processing function"""
        print("🚀 Starting folder reorganization based on names.json\n")
        
        # Load the names mapping
        names_mapping = self.load_names_mapping()
        
        if not names_mapping:
            print("❌ No names mapping found. Please populate names.json")
            print("\nExpected format (EITHER works):")
            print("Format 1 (name: person_id):")
            print(json.dumps({
                "anna": "person_1",
                "lisa": "person_2,person_7",
                "bob": "person_4"
            }, indent=2))
            print("\nFormat 2 (person_id: name):")
            print(json.dumps({
                "person_1": "anna",
                "person_2": "lisa",
                "person_4": "bob"
            }, indent=2))
            return
        
        # Get all existing person folders
        all_person_folders = {f.name: f for f in self.get_all_person_folders()}
        
        # Detect format: check if keys are person_X or names
        first_key = list(names_mapping.keys())[0]
        if first_key.startswith('person_'):
            # Format: "person_1": "anna" - use as-is
            print(f"📋 Detected format: person_id → name")
            final_mapping = names_mapping
        else:
            # Format: "anna": "person_1" or "lisa": "person_2,person_7" - swap it
            print(f"📋 Detected format: name → person_id (swapping...)")
            final_mapping = {}
            for name, person_ids in names_mapping.items():
                if ',' in person_ids:
                    # Multiple person_ids for same name (merge case)
                    for person_id in person_ids.split(','):
                        person_id = person_id.strip()
                        final_mapping[person_id] = name
                else:
                    # Single person_id
                    final_mapping[person_ids] = name
        
        print(f"📋 Processing {len(final_mapping)} name mappings\n")
        processed_folders = set()
        
        # Group person_ids by name to detect merges
        name_to_persons = defaultdict(list)
        to_delete = []
        for person_id, name in final_mapping.items():
            if name and name.strip():
                name_to_persons[name].append(person_id)
            else:
                # null or empty name means delete
                to_delete.append(person_id)
        
        # Delete folders marked as null/empty
        for person_id in to_delete:
            if person_id in all_person_folders:
                print(f"🔄 Processing: {person_id} (marked for deletion)")
                self.delete_folder(all_person_folders[person_id])
                processed_folders.add(person_id)
                print()
        
        # Process each unique name
        for name, person_ids in name_to_persons.items():
            print(f"🔄 Processing: {name}")
            
            # Get folders that exist
            existing_folders = []
            for person_id in person_ids:
                if person_id in all_person_folders:
                    existing_folders.append(all_person_folders[person_id])
                    processed_folders.add(person_id)
                else:
                    print(f"  ⚠️  Folder not found: {person_id}, skipping")
            
            if not existing_folders:
                print(f"  ⚠️  No valid folders found for '{name}'")
                continue
            
            # If multiple person_ids map to same name, merge them
            if len(existing_folders) > 1:
                print(f"  🔀 Merging {len(existing_folders)} folders into '{name}'")
                self.merge_folders(existing_folders, name)
            else:
                # Single folder, just rename
                self.rename_folder(existing_folders[0], name)
            
            print()
        
        # Delete any unprocessed person folders (not in names.json)
        print("🧹 Cleaning up unprocessed folders...\n")
        unprocessed = set(all_person_folders.keys()) - processed_folders
        
        if unprocessed:
            for person_id in unprocessed:
                folder = all_person_folders[person_id]
                print(f"🔄 Processing unmentioned folder: {person_id}")
                self.delete_folder(folder)
                print()
        else:
            print("  ✅ All folders were processed\n")
        
        print("="*60)
        print("✨ Folder reorganization complete!")
        print("="*60)
        
        # Print final structure
        self.print_final_structure()
    
    def print_final_structure(self):
        """Print the final folder structure"""
        print("\n📁 Final folder structure:\n")
        
        people_folders = sorted([f for f in self.people_path.iterdir() 
                                if f.is_dir() and f.name != '__pycache__'])
        
        if not people_folders:
            print("  (No people folders found)")
        else:
            for folder in people_folders:
                face_count = len(list(folder.glob('face_*.jpg')))
                print(f"  📂 {folder.name}/ ({face_count} images)")

def main():
    # Paths
    people_path = "pre_processed/data/people"
    names_json_path = "pre_processed/data/people/names.json"
    
    print("="*60)
    print("People Folder Editor - Based on names.json")
    print("="*60)
    print()
    
    try:
        editor = PeopleFolderEditor(people_path, names_json_path)
        editor.process_names_mapping()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
