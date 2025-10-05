import os, json, csv
from urllib.parse import quote
from pathlib import Path
from dotenv import load_dotenv

# Use shared GCS client
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from lib.gcs_client import get_gcs_client

load_dotenv()

def normalize_key(filename):
    """Normalize filename to match context.json keys by replacing space before AM/PM with non-breaking space"""
    # Remove extension
    fname_without_ext = os.path.splitext(filename)[0]
    # Replace space before AM/PM with unicode non-breaking space (U+202F)
    # This handles patterns like "3.37.37 PM" -> "3.37.37\u202fPM"
    fname_without_ext = fname_without_ext.replace(' PM', '\u202fPM')
    fname_without_ext = fname_without_ext.replace(' AM', '\u202fAM')
    return fname_without_ext

def build_rows():
    rows = []
    client, bucket = get_gcs_client()
    blobs = list(bucket.list_blobs())
    events = set("/".join(blob.name.split("/")[:1]) for blob in blobs if "/" in blob.name)

    for event in events:
        ctx_blob = bucket.blob(f"{event}/context.json")
        if not ctx_blob.exists():
            print(f"⚠️ No context.json found for {event}")
            continue

        ctx = json.loads(ctx_blob.download_as_text())
        event_summary = ctx.get("memory_context", "")

        for blob in bucket.list_blobs(prefix=f"{event}/"):
            if blob.name.endswith("/") or "context.json" in blob.name or blob.name.endswith(".DS_Store"):
                continue

            fname = blob.name.split("/")[-1]
            ftype = "video" if fname.endswith((".mp4", ".mov")) else "image"

            # Normalize the filename to match context keys (handle unicode spaces)
            normalized_name = normalize_key(fname)
            context_key = f"{normalized_name}_context"
            people_key = f"{normalized_name}_people"

            description = ctx.get(context_key, "")
            people_value = ctx.get(people_key, "none")

            # Convert people to JSON array format
            if isinstance(people_value, str):
                if people_value.lower() == "none" or people_value.lower() == "unknown":
                    people = []
                else:
                    people = [people_value]
            elif isinstance(people_value, list):
                people = people_value
            else:
                people = []

            file_url = f"https://storage.googleapis.com/{BUCKET}/{quote(blob.name)}"

            rows.append({
                "event_name": event,
                "file_name": fname,
                "file_type": ftype,
                "description": description,
                "people": json.dumps(people),
                "event_summary": event_summary,
                "file_url": file_url
            })

    return rows

def main():
    rows = build_rows()
    out_path = Path("data/metadata.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "event_name","file_name","file_type","description","people","event_summary","file_url"
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Wrote {len(rows)} rows to {out_path}")

if __name__ == "__main__":
    main()
