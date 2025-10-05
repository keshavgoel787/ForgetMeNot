"""Snowflake database client for memory vault operations."""

import snowflake.connector
from .config import Config


class SnowflakeClient:
    """Client for interacting with Snowflake MEMORY_VAULT table."""

    def __init__(self, config=None):
        """
        Initialize Snowflake client.

        Args:
            config: Dictionary of Snowflake connection parameters.
                   Defaults to Config.SNOWFLAKE_CONFIG if not provided.
        """
        self.config = config or Config.SNOWFLAKE_CONFIG
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish connection to Snowflake."""
        self.conn = snowflake.connector.connect(**self.config)
        self.cursor = self.conn.cursor()
        print("✅ Connected to Snowflake")
        return self

    def insert_clip_with_embedding(self, clip_data):
        """
        Insert a memory clip into MEMORY_VAULT with generated embedding.

        Args:
            clip_data: Dictionary containing clip metadata with keys:
                - id, title, clip_name, description, scene_label,
                  emotion_label, context_tags_json, clip_url

        Returns:
            True if successful, False otherwise
        """
        try:
            self.cursor.execute("""
                INSERT INTO MEMORY_VAULT (
                    id, title, clip_name, description, scene_label,
                    emotion_label, context_tags, clip_url, embedding
                )
                SELECT %s, %s, %s, %s, %s, %s, PARSE_JSON(%s), %s,
                       SNOWFLAKE.CORTEX.EMBED_TEXT_768(%s, %s)
            """, (
                clip_data["id"],
                clip_data["title"],
                clip_data["clip_name"],
                clip_data["description"],
                clip_data["scene_label"],
                clip_data["emotion_label"],
                clip_data["context_tags_json"],
                clip_data["clip_url"],
                Config.EMBEDDING_MODEL,
                clip_data["description"]  # Text to embed
            ))
            return True
        except Exception as e:
            print(f"❌ Insert failed for {clip_data['clip_name']}: {e}")
            return False

    def commit(self):
        """Commit pending transactions."""
        if self.conn:
            self.conn.commit()

    def close(self):
        """Close database connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
