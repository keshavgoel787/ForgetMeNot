"""
Search for memories using Cortex semantic similarity.

This script demonstrates Phase 1: Cortex-based retrieval.
Users can enter natural-language queries to find relevant memory clips.
"""

import sys
sys.path.append('..')

from lib.config import Config
from lib.snowflake_client import SnowflakeClient


def get_cortex_embedding(text, cursor):
    """
    Generate embedding for text using Snowflake Cortex.

    Args:
        text: String to embed
        cursor: Active Snowflake cursor

    Returns:
        List of floats representing the embedding vector
    """
    cursor.execute("""
        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(%s, %s)::ARRAY
    """, (Config.EMBEDDING_MODEL, text))

    result = cursor.fetchone()
    return result[0] if result else None


def search_memories(query, client, top_k=3):
    """
    Search for memories semantically similar to the query.

    Args:
        query: Natural language search query
        client: Connected SnowflakeClient instance
        top_k: Number of top results to return (default: 3)

    Returns:
        List of tuples (title, description, clip_url, similarity_score)
    """
    print(f"\n🔍 Searching for: '{query}'")

    # Get query embedding
    query_embedding = get_cortex_embedding(query, client.cursor)

    if not query_embedding:
        print("❌ Failed to generate embedding for query")
        return []

    print(f"✅ Generated embedding (dimension: {len(query_embedding)})")

    # Search using vector similarity
    # Use the embedding directly - Snowflake handles the conversion
    client.cursor.execute("""
        SELECT
            title,
            description,
            clip_url,
            scene_label,
            emotion_label,
            VECTOR_COSINE_SIMILARITY(embedding, SNOWFLAKE.CORTEX.EMBED_TEXT_768(%s, %s)) AS similarity
        FROM MEMORY_VAULT
        ORDER BY similarity DESC
        LIMIT %s
    """, (Config.EMBEDDING_MODEL, query, top_k))

    results = client.cursor.fetchall()

    # Display results
    print(f"\n📊 Found {len(results)} results:\n")

    for i, (title, desc, url, scene, emotion, score) in enumerate(results, 1):
        print(f"{'='*70}")
        print(f"🎬 Result #{i} (Similarity: {score:.4f})")
        print(f"{'='*70}")
        print(f"Title:       {title}")
        print(f"Scene:       {scene}")
        print(f"Emotion:     {emotion}")
        print(f"Description: {desc}")
        print(f"URL:         {url}")
        print()

    return results


def interactive_search():
    """Run interactive search loop."""
    print("🧠 ReMind Memory Search (Phase 1: Cortex Retrieval)")
    print("="*70)

    with SnowflakeClient() as client:
        while True:
            print("\n" + "="*70)
            query = input("💭 Enter your memory query (or 'quit' to exit): ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if not query:
                print("⚠️  Please enter a query")
                continue

            search_memories(query, client)


def test_queries():
    """Test with sample queries."""
    print("🧠 ReMind Memory Search — Testing Sample Queries")
    print("="*70)

    test_queries_list = [
        "the day at Disney beach with Anna",
        "Anna and I at the boardwalk eating hotdogs",
        "our football game trip",
        "college day with friends"
    ]

    with SnowflakeClient() as client:
        for query in test_queries_list:
            search_memories(query, client, top_k=2)
            input("\nPress Enter to continue to next query...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Search memories using Cortex')
    parser.add_argument('--test', action='store_true',
                       help='Run test queries instead of interactive mode')
    parser.add_argument('--query', type=str,
                       help='Single query to run (non-interactive)')
    parser.add_argument('--top-k', type=int, default=3,
                       help='Number of results to return (default: 3)')

    args = parser.parse_args()

    if args.test:
        test_queries()
    elif args.query:
        with SnowflakeClient() as client:
            search_memories(args.query, client, top_k=args.top_k)
    else:
        interactive_search()
