"""
Upload memory clip metadata to Snowflake MEMORY_VAULT table.

This script reads metadata from a CSV file and uploads it to Snowflake,
generating embeddings using Snowflake Cortex for semantic search.
"""

from lib.config import Config
from lib.snowflake_client import SnowflakeClient
from lib.data_processor import load_metadata, prepare_clip_data


def process_clips(df, client, parallel=True, max_workers=4):
    """
    Process all clips from DataFrame and insert into Snowflake.

    Args:
        df: pandas DataFrame with clip metadata
        client: SnowflakeClient instance
        parallel: If True, use parallel processing (default: True)
        max_workers: Number of parallel workers (default: 4)

    Returns:
        Tuple of (success_count, failure_count)
    """
    # Prepare all clip data
    clips_data = []
    skip_count = 0

    for _, row in df.iterrows():
        clip_data = prepare_clip_data(row)
        if clip_data is None:
            skip_count += 1
            continue

        print(f"🧩 Prepared: {clip_data['clip_name']}")
        print(f"   {clip_data['description'][:60]}...")
        clips_data.append(clip_data)

    if not clips_data:
        return 0, skip_count

    # Insert clips (parallel or sequential)
    print(f"\n{'⚡ Parallel' if parallel else '📝 Sequential'} upload starting...")

    if parallel:
        success, failure = client.batch_insert_clips(clips_data, max_workers)
    else:
        success = 0
        failure = 0
        for clip in clips_data:
            if client.insert_clip_with_embedding(clip):
                print(f"✅ Inserted {clip['clip_name']} with embedding")
                success += 1
            else:
                failure += 1

    return success, failure + skip_count


def main(parallel=True, max_workers=4):
    """
    Main execution function.

    Args:
        parallel: Enable parallel processing (default: True)
        max_workers: Number of parallel workers (default: 4)
    """
    import time

    # Load metadata
    df = load_metadata(Config.METADATA_CSV_PATH)

    # Upload clips using context manager
    start_time = time.time()

    with SnowflakeClient() as client:
        success_count, failure_count = process_clips(
            df, client, parallel=parallel, max_workers=max_workers
        )
        client.commit()

    elapsed = time.time() - start_time

    # Print summary
    print("\n" + "="*50)
    print(f"🎉 Upload complete in {elapsed:.2f}s!")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed:  {failure_count}")
    print("="*50)


if __name__ == "__main__":
    main()
