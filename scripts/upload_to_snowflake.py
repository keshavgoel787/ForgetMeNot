"""
Upload memory clip metadata to Snowflake MEMORY_VAULT table.

This script reads metadata from a CSV file and uploads it to Snowflake,
generating embeddings using Snowflake Cortex for semantic search.
"""

from lib.config import Config
from lib.snowflake_client import SnowflakeClient
from lib.data_processor import load_metadata, prepare_clip_data


def process_clips(df, client):
    """
    Process all clips from DataFrame and insert into Snowflake.

    Args:
        df: pandas DataFrame with clip metadata
        client: SnowflakeClient instance

    Returns:
        Tuple of (success_count, failure_count)
    """
    success_count = 0
    failure_count = 0

    for _, row in df.iterrows():
        clip_data = prepare_clip_data(row)

        if clip_data is None:
            failure_count += 1
            continue

        print(f"🧩 Processing: {clip_data['clip_name']}")
        print(f"   {clip_data['description'][:60]}...")

        if client.insert_clip_with_embedding(clip_data):
            print(f"✅ Inserted {clip_data['clip_name']} with embedding")
            success_count += 1
        else:
            failure_count += 1

    return success_count, failure_count


def main():
    """Main execution function."""
    # Load metadata
    df = load_metadata(Config.METADATA_CSV_PATH)

    # Upload clips using context manager
    with SnowflakeClient() as client:
        success_count, failure_count = process_clips(df, client)
        client.commit()

    # Print summary
    print("\n" + "="*50)
    print(f"🎉 Upload complete!")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed:  {failure_count}")
    print("="*50)


if __name__ == "__main__":
    main()
