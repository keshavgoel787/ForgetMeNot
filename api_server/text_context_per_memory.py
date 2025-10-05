import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

class MemoryContextAnalyzer:
    def __init__(self, api_key: str, people_path: str = "pre_processed/data/people"):
        """Initialize the analyzer with Gemini API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        self.people_path = Path(people_path)
        
        # Supported file extensions
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        
        # Load people reference images
        self.people_references = self.load_people_references()
    
    def load_people_references(self):
        """Load reference images for each person"""
        people_refs = {}
        
        if not self.people_path.exists():
            print(f"⚠️  People folder not found: {self.people_path}")
            return people_refs
        
        for person_folder in self.people_path.iterdir():
            if person_folder.is_dir() and not person_folder.name.startswith('.'):
                person_name = person_folder.name
                # Get up to 3 reference images for each person
                ref_images = []
                for img_file in sorted(person_folder.glob('face_*.jpg'))[:3]:
                    try:
                        ref_images.append(Image.open(img_file))
                    except Exception as e:
                        print(f"⚠️  Could not load reference image: {img_file}")
                
                if ref_images:
                    people_refs[person_name] = ref_images
                    print(f"  👤 Loaded {len(ref_images)} reference images for {person_name}")
        
        return people_refs
    
    def analyze_image(self, image_path: str) -> dict:
        """Analyze a single image and return contextual description and people list"""
        try:
            print(f"  📸 Analyzing image: {Path(image_path).name}")
            image = Image.open(image_path)
            
            # Build prompt with people references
            prompt_parts = []
            
            if self.people_references:
                prompt_parts.append("You are analyzing images/videos that may contain the following people. Here are reference images:")
                prompt_parts.append("")
                for person_name, ref_images in self.people_references.items():
                    prompt_parts.append(f"Person name: {person_name}")
                    prompt_parts.append(f"(See {len(ref_images)} reference images of {person_name})")
                    prompt_parts.extend(ref_images)
                prompt_parts.append("")
            
            prompt_parts.append("""Now analyze this image. Provide your response in this EXACT format:

CONTEXT:
[Describe what's happening in the scene, activities, setting, location, environment, objects, mood, and atmosphere in 2-3 sentences. IMPORTANT: Use the actual NAMES of people you recognize in the description (e.g., "Anna and Lisa shopping" not "two friends shopping"). If you don't recognize someone, use "an unknown person". DO NOT include phrases like 'here is the context' or 'the image shows' - just write the direct description.]

PEOPLE:
[List the names of people you recognize from the reference images, separated by commas. If you see people but don't recognize them, write 'unknown'. If no people visible, write 'none'.]""")
            
            prompt_parts.append(image)
            
            response = self.model.generate_content(prompt_parts)
            result_text = response.text.strip()
            
            # Parse response
            context = ""
            people = ""
            
            if "CONTEXT:" in result_text and "PEOPLE:" in result_text:
                parts = result_text.split("PEOPLE:")
                context_part = parts[0].replace("CONTEXT:", "").strip()
                people_part = parts[1].strip() if len(parts) > 1 else ""
                
                context = context_part
                people = people_part
            else:
                context = result_text
                people = "unknown"
            
            return {
                "context": context,
                "people": people
            }
            
        except Exception as e:
            print(f"  ❌ Error analyzing image: {str(e)}")
            return {
                "context": f"Error: {str(e)}",
                "people": "unknown"
            }
    
    def analyze_video(self, video_path: str) -> dict:
        """Analyze a video with both visual and audio content"""
        try:
            print(f"  🎥 Analyzing video: {Path(video_path).name}")
            
            # Build prompt with people references
            prompt_parts = []
            
            if self.people_references:
                prompt_parts.append("You are analyzing images/videos that may contain the following people. Here are reference images:")
                prompt_parts.append("")
                for person_name, ref_images in self.people_references.items():
                    prompt_parts.append(f"Person name: {person_name}")
                    prompt_parts.append(f"(See {len(ref_images)} reference images of {person_name})")
                    prompt_parts.extend(ref_images)
                prompt_parts.append("")
            
            prompt_parts.append("""Now analyze this video comprehensively including both visual and audio content.

Provide your response in this EXACT format:

CONTEXT:
[Describe the main activities, events, people, setting, environment, key dialogue, spoken words, background sounds, audio atmosphere, and the overall story/experience this captures. Write 3-4 sentences. IMPORTANT: Use the actual NAMES of people you recognize in the description (e.g., "Anna and Lisa shopping at Target" not "two women shopping"). If you don't recognize someone, use "an unknown person". DO NOT include phrases like 'here is the context' or 'the video shows' - just write the direct description.]

PEOPLE:
[List the names of people you recognize from the reference images, separated by commas. If you see people but don't recognize them, write 'unknown'. If no people visible, write 'none'.]""")
            
            # Upload video file for processing
            video_file = genai.upload_file(video_path)
            print(f"     Uploaded, processing...")
            
            # Wait for video processing to complete
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                return {
                    "context": "Video processing failed",
                    "people": "unknown"
                }
            
            prompt_parts.append(video_file)
            
            response = self.model.generate_content(prompt_parts)
            result_text = response.text.strip()
            
            # Clean up uploaded file
            genai.delete_file(video_file.name)
            
            # Parse response
            context = ""
            people = ""
            
            if "CONTEXT:" in result_text and "PEOPLE:" in result_text:
                parts = result_text.split("PEOPLE:")
                context_part = parts[0].replace("CONTEXT:", "").strip()
                people_part = parts[1].strip() if len(parts) > 1 else ""
                
                context = context_part
                people = people_part
            else:
                context = result_text
                people = "unknown"
            
            return {
                "context": context,
                "people": people
            }
            
        except Exception as e:
            print(f"  ❌ Error analyzing video: {str(e)}")
            return {
                "context": f"Error: {str(e)}",
                "people": "unknown"
            }
    
    def process_memory_folder(self, folder_path: str):
        """Process all images and videos in a memory folder"""
        folder_name = Path(folder_path).name
        print(f"\n🗂️  Processing memory folder: {folder_name}")
        
        # Load existing context.json if it exists
        context_file = Path(folder_path) / "context.json"
        context_data = {}
        
        if context_file.exists():
            try:
                with open(context_file, 'r') as f:
                    context_data = json.load(f)
            except Exception as e:
                print(f"  ⚠️  Could not load existing context.json: {e}")
        
        # Process all media files
        file_contexts = {}
        
        for file_path in sorted(Path(folder_path).iterdir()):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                
                if ext in self.image_extensions:
                    result = self.analyze_image(str(file_path))
                    file_contexts[f"{file_path.stem}_context"] = result["context"]
                    file_contexts[f"{file_path.stem}_people"] = result["people"]
                    
                elif ext in self.video_extensions:
                    result = self.analyze_video(str(file_path))
                    file_contexts[f"{file_path.stem}_context"] = result["context"]
                    file_contexts[f"{file_path.stem}_people"] = result["people"]
        
        # Update context data with file contexts
        context_data.update(file_contexts)
        
        # Save updated context.json
        with open(context_file, 'w') as f:
            json.dump(context_data, f, indent=2)
        
        file_count = len([k for k in file_contexts.keys() if k.endswith('_context')])
        print(f"  ✅ Updated context.json with {file_count} files (context + people)")
    
    def process_all_memories(self, memories_base_path: str):
        """Process all memory folders"""
        memories_path = Path(memories_base_path)
        
        if not memories_path.exists():
            print(f"❌ Memories path not found: {memories_base_path}")
            return
        
        print(f"\n🚀 Starting analysis of all memories in: {memories_base_path}")
        
        memory_folders = [f for f in memories_path.iterdir() if f.is_dir()]
        
        for i, memory_folder in enumerate(memory_folders, 1):
            print(f"\n{'='*60}")
            print(f"Processing folder {i}/{len(memory_folders)}: {memory_folder.name}")
            print(f"{'='*60}")
            self.process_memory_folder(str(memory_folder))
        
        print(f"\n\n✨ Analysis complete! Processed {len(memory_folders)} memory folders.")

def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("Please create a .env file with your API key:")
        print("GEMINI_API_KEY=your_api_key_here")
        return
    
    # Initialize analyzer
    people_path = "pre_processed/data/people"
    analyzer = MemoryContextAnalyzer(api_key, people_path)
    
    print("\n" + "="*60)
    print("Loading people references...")
    print("="*60)
    
    # Path to memories folder
    memories_path = "pre_processed/data/memories"
    
    # Process all memories
    analyzer.process_all_memories(memories_path)

if __name__ == "__main__":
    main()
