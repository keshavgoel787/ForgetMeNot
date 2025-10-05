"""
Snowflake Upload API routes
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
import sys
import os

# Use shared GCS client
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
from scripts.lib.gcs_client import get_gcs_client
import pandas as pd
import json
import uuid
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from scripts.lib.snowflake_client import SnowflakeClient
from scripts.lib.config import Config
from api.schemas import UploadMetadataRequest, UploadMetadataResponse, FileUploadResponse, ErrorResponse

router = APIRouter(prefix="/admin/upload", tags=["Admin"])


@router.post("/snowflake", response_model=UploadMetadataResponse)
async def upload_metadata_to_snowflake(request: UploadMetadataRequest):
    """
    Upload metadata CSV to Snowflake MEMORY_VAULT table.

    This endpoint:
    1. Reads metadata from CSV file (default: data/metadata.csv)
    2. Optionally truncates existing data in MEMORY_VAULT
    3. Inserts records with embeddings using CORTEX.EMBED_TEXT_768
    4. Returns upload statistics

    **Parameters:**
    - **csv_path**: Path to metadata CSV (default: data/metadata.csv)
    - **truncate_existing**: Clear existing data before upload (default: true)
    """
    try:
        csv_path = Path(request.csv_path)

        if not csv_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"CSV file not found at {csv_path}. Run /metadata/build first."
            )

        # Read CSV
        df = pd.read_csv(csv_path)
        total_records = len(df)

        if total_records == 0:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty. No records to upload."
            )

        # Connect to Snowflake
        with SnowflakeClient() as client:
            # Truncate if requested
            if request.truncate_existing:
                client.cursor.execute("TRUNCATE TABLE MEMORY_VAULT")
                client.conn.commit()

            success_count = 0
            skip_count = 0

            # Upload records
            for idx, row in df.iterrows():
                desc = str(row["description"]).strip() if pd.notna(row["description"]) else ""
                summary = str(row.get("event_summary", "")).strip() if pd.notna(row.get("event_summary", "")) else ""
                file_type = str(row["file_type"]).strip() if pd.notna(row["file_type"]) else ""
                file_url = str(row["file_url"]).strip() if pd.notna(row["file_url"]) else ""

                # Remove surrounding quotes if present (from CSV parsing)
                if desc.startswith('"') and desc.endswith('"'):
                    desc = desc[1:-1]
                if summary.startswith('"') and summary.endswith('"'):
                    summary = summary[1:-1]

                # Generate embedding using description (prioritize description over summary)
                text_for_embedding = desc or summary

                if not text_for_embedding or text_for_embedding == "nan":
                    skip_count += 1
                    continue

                # Parse people JSON string to array
                people_json = row["people"] if pd.notna(row["people"]) else "[]"
                people_list = json.loads(people_json)
                people_sql = json.dumps(people_list)

                # Use Snowflake CORTEX function to generate embedding directly in SQL
                sql = """
                    INSERT INTO MEMORY_VAULT
                    (id, event_name, file_name, file_type, description, people, event_summary, file_url, embedding)
                    SELECT %s,%s,%s,%s,%s,PARSE_JSON(%s)::ARRAY,%s,%s,
                           SNOWFLAKE.CORTEX.EMBED_TEXT_768(%s, %s)
                """

                try:
                    client.cursor.execute(sql, (
                        str(uuid.uuid4()),
                        row["event_name"] if pd.notna(row["event_name"]) else "",
                        row["file_name"] if pd.notna(row["file_name"]) else "",
                        file_type,
                        desc,
                        people_sql,
                        summary,
                        file_url,
                        Config.EMBEDDING_MODEL,
                        text_for_embedding
                    ))
                    success_count += 1
                except Exception as e:
                    skip_count += 1
                    continue

                # Commit every 10 records
                if (idx + 1) % 10 == 0:
                    client.conn.commit()

            # Final commit
            client.conn.commit()

        return UploadMetadataResponse(
            status="success",
            records_uploaded=success_count,
            records_skipped=skip_count,
            total_records=total_records,
            message=f"Successfully uploaded {success_count}/{total_records} records to Snowflake"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload to Snowflake failed: {str(e)}")


@router.post("/gcs", response_model=FileUploadResponse)
async def upload_file_to_gcs(
    file: UploadFile = File(...),
    event_name: str = "general"
):
    """
    Upload a video or image file to Google Cloud Storage.

    This endpoint:
    1. Accepts a file upload (video/image)
    2. Uploads to GCS bucket in the specified event folder
    3. Returns the public URL

    **Parameters:**
    - **file**: Video or image file to upload
    - **event_name**: Event folder name (default: "general")
    """
    try:
        # Validate file type
        file_extension = file.filename.split(".")[-1].lower()
        valid_video_extensions = ["mp4", "mov", "avi", "mkv"]
        valid_image_extensions = ["jpg", "jpeg", "png", "gif", "webp"]

        if file_extension in valid_video_extensions:
            file_type = "video"
        elif file_extension in valid_image_extensions:
            file_type = "image"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Supported: {valid_video_extensions + valid_image_extensions}"
            )

        # Use shared GCS client
        gcs_client, bucket = get_gcs_client()

        # Create blob path
        blob_name = f"{event_name}/{file.filename}"
        blob = bucket.blob(blob_name)

        # Upload file
        contents = await file.read()
        blob.upload_from_string(contents, content_type=file.content_type)

        # Generate public URL
        bucket_name = os.getenv("GCS_BUCKET", "forgetmenot-videos")
        file_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"

        return FileUploadResponse(
            status="success",
            file_url=file_url,
            bucket=bucket_name,
            blob_name=blob_name,
            event_name=event_name,
            file_type=file_type,
            message=f"Successfully uploaded {file.filename} to {event_name}/"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload to GCS failed: {str(e)}")
