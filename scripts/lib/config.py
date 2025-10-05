"""Configuration management for Snowflake connection."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration settings for Snowflake and data paths."""

    # Snowflake connection
    SNOWFLAKE_CONFIG = {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA")
    }

    # Data paths
    METADATA_CSV_PATH = "../data/metadata.csv"
    CLIP_URL_BASE = "https://storage.googleapis.com/forgetmenot-videos/"

    # Embedding model
    EMBEDDING_MODEL = "e5-base-v2"
