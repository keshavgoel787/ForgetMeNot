"""
Metadata Management API routes for GCS and Snowflake operations
"""
from fastapi import APIRouter, HTTPException
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from scripts.build_metadata_from_context import build_rows
from api.schemas import BuildMetadataResponse, MetadataRow, ErrorResponse

router = APIRouter(prefix="/admin/metadata", tags=["Admin"])


@router.post("/build", response_model=BuildMetadataResponse)
async def build_metadata_from_gcs():
    """
    Build metadata CSV from GCS context.json files.

    This endpoint:
    1. Scans all event folders in GCS bucket
    2. Reads context.json files from each folder
    3. Generates metadata.csv with file information, descriptions, and people
    4. Returns the generated metadata

    The CSV will be saved to `data/metadata.csv`.
    """
    try:
        # Build rows from GCS
        rows = build_rows()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No metadata found in GCS bucket. Ensure context.json files exist in event folders."
            )

        # Save to CSV
        import csv
        from pathlib import Path
        import json

        out_path = Path("data/metadata.csv")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "event_name", "file_name", "file_type", "description",
                "people", "event_summary", "file_url"
            ])
            writer.writeheader()
            writer.writerows(rows)

        # Convert rows to MetadataRow models
        metadata_results = []
        for row in rows:
            people_list = json.loads(row["people"]) if isinstance(row["people"], str) else row["people"]
            metadata_results.append(MetadataRow(
                event_name=row["event_name"],
                file_name=row["file_name"],
                file_type=row["file_type"],
                description=row["description"],
                people=people_list,
                event_summary=row["event_summary"],
                file_url=row["file_url"]
            ))

        return BuildMetadataResponse(
            status="success",
            rows_generated=len(rows),
            metadata=metadata_results,
            csv_path=str(out_path.absolute()),
            message=f"Successfully generated {len(rows)} metadata rows from GCS"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metadata building failed: {str(e)}")


@router.get("/count")
async def get_metadata_count():
    """
    Get count of metadata rows in existing CSV file.
    """
    try:
        import pandas as pd
        from pathlib import Path

        csv_path = Path("data/metadata.csv")

        if not csv_path.exists():
            return {
                "status": "not_found",
                "count": 0,
                "message": "No metadata.csv found. Run /metadata/build first."
            }

        df = pd.read_csv(csv_path)
        return {
            "status": "success",
            "count": len(df),
            "csv_path": str(csv_path.absolute()),
            "message": f"Found {len(df)} metadata rows"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read metadata: {str(e)}")
