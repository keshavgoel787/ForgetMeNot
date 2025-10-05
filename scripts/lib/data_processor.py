"""Data processing utilities for memory clip metadata."""

import uuid
import json
import pandas as pd
from .config import Config


def load_metadata(csv_path=None):
    """
    Load metadata from CSV file.

    Args:
        csv_path: Path to CSV file. Defaults to Config.METADATA_CSV_PATH

    Returns:
        pandas DataFrame with metadata
    """
    path = csv_path or Config.METADATA_CSV_PATH
    df = pd.read_csv(path)
    print(f"📚 Loaded {len(df)} rows from metadata.csv")
    return df


def validate_description(description):
    """
    Validate and clean description text.

    Args:
        description: Raw description value from CSV

    Returns:
        Cleaned description string or None if invalid
    """
    if isinstance(description, str):
        cleaned = description.strip()
    elif pd.notna(description):
        cleaned = str(description).strip()
    else:
        cleaned = ""

    return cleaned if cleaned else None


def parse_context_tags(tags_str):
    """
    Parse context tags from string representation of list.

    Args:
        tags_str: String like "['tag1', 'tag2']"

    Returns:
        JSON string of tags array
    """
    try:
        tags_list = eval(tags_str) if tags_str else []
        return json.dumps(tags_list)
    except:
        return json.dumps([])


def prepare_clip_data(row):
    """
    Prepare clip data dictionary from CSV row.

    Args:
        row: pandas DataFrame row

    Returns:
        Dictionary with clip data or None if invalid
    """
    description = validate_description(row.get("description", ""))

    if not description:
        print(f"⚠️  Skipping {row.get('clip_name', '(unknown)')} - empty description")
        return None

    clip_name = row.get("clip_name", f"clip_{uuid.uuid4()}.mp4")

    return {
        "id": str(uuid.uuid4()),
        "title": row.get("title", "Untitled"),
        "clip_name": clip_name,
        "description": description,
        "scene_label": row.get("scene_label", "unknown"),
        "emotion_label": row.get("emotion_label", "neutral"),
        "context_tags_json": parse_context_tags(row.get("context_tags", "[]")),
        "clip_url": f"{Config.CLIP_URL_BASE}{clip_name}"
    }
