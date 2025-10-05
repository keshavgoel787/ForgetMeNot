"""Shared Google Cloud Storage client for ReMind."""

import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

# Global client instance
_client = None
_bucket = None

BUCKET_NAME = os.getenv("GCS_BUCKET", "forgetmenot-videos")


def get_gcs_client():
    """
    Get or create GCS client (lazy loading).

    Returns:
        Tuple[storage.Client, storage.Bucket]: GCS client and bucket
    """
    global _client, _bucket

    if _client is None:
        _client = storage.Client()
        _bucket = _client.bucket(BUCKET_NAME)

    return _client, _bucket


def get_bucket():
    """Get GCS bucket instance."""
    _, bucket = get_gcs_client()
    return bucket
