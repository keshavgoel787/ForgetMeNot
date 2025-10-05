# People Folder Editor

Reorganize person folders based on a `names.json` mapping file.

## What It Does

This script reads `names.json` and:
1. **Renames** person folders (e.g., `person_1` → `anna`)
2. **Merges** folders when multiple person IDs map to same person
3. **Deletes** folders marked as null or empty
4. **Cleans up** any person folders not mentioned in names.json

## Usage

### 1. Create/Edit names.json

Edit `pre_processed/data/people/names.json`:

```json
{
  "person_1": "anna",
  "person_2": "lisa",
  "person_3": "john",
  "person_4": null,
  "person_5": ""
}
```

### 2. Run the Script

```bash
cd processing_script
source venv/bin/activate
python edit_pictures_based_on_json.py
```

## names.json Format

### **Single Name** - Rename folder
```json
{
  "person_1": "anna"
}
```
Result: `person_1/` → `anna/`

---

### **Merge Person Folders** - Combine two misidentified people
```json
{
  "person_1": "anna",
  "person_3": "person_1,person_3"
}
```
Result: Merges `person_1/` and `person_3/` into `merged_person_3/`

---

### **Multiple Names (Aliases)** - Person has nicknames
```json
{
  "person_2": "sarah,sally"
}
```
Result: `person_2/` → `sarah/` (uses first name)

---

### **Delete Folder** - Unwanted/unknown person
```json
{
  "person_4": null
}
```
or
```json
{
  "person_4": ""
}
```
Result: `person_4/` is deleted

---

### **Not Mentioned** - Auto-delete
If a person folder is not in names.json at all, it will be **deleted automatically**.

## Examples

### Example 1: Simple Renaming

**Before:**
```
people/
├── person_1/
├── person_2/
└── person_3/
```

**names.json:**
```json
{
  "person_1": "anna",
  "person_2": "lisa",
  "person_3": "john"
}
```

**After:**
```
people/
├── anna/
├── lisa/
└── john/
```

---

### Example 2: Merge + Delete

**Before:**
```
people/
├── person_1/  (50 images of Anna)
├── person_2/  (30 images of Anna - misidentified)
├── person_3/  (20 images of stranger)
└── person_4/  (40 images of Lisa)
```

**names.json:**
```json
{
  "person_1": "anna",
  "person_2": "person_1,person_2",
  "person_3": null,
  "person_4": "lisa"
}
```

**After:**
```
people/
├── anna/  (50 images)
├── merged_person_2/  (80 images - person_1 + person_2)
└── lisa/  (40 images)
```

---

### Example 3: Cleanup Unknowns

**Before:**
```
people/
├── person_1/
├── person_2/
├── person_3/
└── person_4/
```

**names.json:**
```json
{
  "person_1": "anna",
  "person_2": "lisa"
}
```

**After:**
```
people/
├── anna/
└── lisa/
```
(person_3 and person_4 automatically deleted)

## What Gets Preserved

The script preserves:
- ✅ All face images (`face_XXXX.jpg`)
- ✅ Metadata (`metadata.json` - updated with new name)
- ✅ Source information (which videos/memories each face came from)

## Safety Tips

1. **Backup first!** Copy your `people/` folder before running
2. **Test mode**: Use `people_test/` first to verify it works
3. **Check results**: Review the final structure printed by the script

## Output Example

```
🚀 Starting folder reorganization based on names.json

📋 Loaded 5 name mappings

🔄 Processing: person_1
  📝 Renaming 'person_1' → 'anna'
    ✅ Renamed successfully

🔄 Processing: person_2
  🗑️  Deleting folder: person_2
    ✅ Deleted successfully

🔄 Processing: person_3
  🔀 Merging 2 folders into 'merged_person_3'
    📂 Merging from: person_1
    📂 Merging from: person_3
    ✅ Merged 80 face images
    🗑️  Deleted: person_1
    🗑️  Deleted: person_3

============================================================
✨ Folder reorganization complete!
============================================================

📁 Final folder structure:

  📂 anna/ (161 images)
  📂 lisa/ (115 images)
  📂 merged_person_3/ (80 images)
```

## Troubleshooting

**"names.json is empty!"**
- Create the file with proper JSON mapping

**"Folder already exists"**
- Two person IDs map to the same name
- Use merge syntax instead: `"person_2": "person_1,person_2"`

**Merged wrong people**
- Update names.json to split them back
- Re-run the original clustering with different tolerance
