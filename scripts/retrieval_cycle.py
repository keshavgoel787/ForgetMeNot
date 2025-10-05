"""
Retrieval Cycle: Query → Search → Summarize

This module implements the complete retrieval cycle:
1. User asks a natural language question (e.g., "what did we eat at Disney?")
2. Search Snowflake using vector similarity
3. Use Gemini to synthesize a natural answer from retrieved memories
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.lib.config import Config
from scripts.lib.snowflake_client import SnowflakeClient
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def search_memories_by_query(query: str, client: SnowflakeClient, top_k: int = 5):
    """
    Search for memories using vector similarity.

    Args:
        query: Natural language query
        client: Connected SnowflakeClient
        top_k: Number of results to retrieve

    Returns:
        List of tuples containing memory data
    """
    print(f"\n🔍 Searching for: '{query}'")

    # Search using Cortex embedding and vector similarity
    client.cursor.execute("""
        SELECT
            event_name,
            file_name,
            file_type,
            description,
            people,
            event_summary,
            file_url,
            VECTOR_COSINE_SIMILARITY(
                embedding,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768(%s, %s)
            ) AS similarity
        FROM MEMORY_VAULT
        WHERE description IS NOT NULL AND description != ''
        ORDER BY similarity DESC
        LIMIT %s
    """, (Config.EMBEDDING_MODEL, query, top_k))

    results = client.cursor.fetchall()
    print(f"✅ Found {len(results)} relevant memories\n")

    return results


def format_memories_for_gemini(memories: list) -> str:
    """
    Format retrieved memories into a context string for Gemini.

    Args:
        memories: List of memory tuples from Snowflake

    Returns:
        Formatted string with all memory contexts
    """
    if not memories:
        return "No memories found."

    context_parts = []
    for idx, memory in enumerate(memories, 1):
        event_name, file_name, file_type, description, people, event_summary, file_url, similarity = memory

        # Format people array - filter out empty strings
        if people:
            people_list = [p.strip() for p in people if p and p.strip()]
            people_str = ", ".join(people_list) if people_list else "unknown"
        else:
            people_str = "unknown"

        context_parts.append(f"""
Memory {idx} (Relevance: {similarity:.2f}):
Event: {event_name}
File: {file_name} ({file_type})
People: {people_str}
Description: {description}
Event Summary: {event_summary}
---""")

    return "\n".join(context_parts)


def generate_simple_summary(query: str, memories: list) -> str:
    """
    Generate a simple rule-based summary when Gemini is unavailable.

    Args:
        query: Original user query
        memories: List of memory tuples

    Returns:
        Simple summary string
    """
    if not memories:
        return "I couldn't find any memories matching your question."

    # Extract key information from top memories
    top_memory = memories[0]
    event_name, file_name, file_type, description, people, event_summary, file_url, similarity = top_memory

    # Format people
    if people:
        people_list = [p.strip() for p in people if p and p.strip()]
        people_str = " with " + ", ".join(people_list) if people_list else ""
    else:
        people_str = ""

    # Build summary based on query type
    query_lower = query.lower()

    if "eat" in query_lower or "food" in query_lower:
        summary = f"Looking at your {event_name} memories{people_str}, I can see: {description}"
    elif "who" in query_lower:
        if people_str:
            summary = f"From your {event_name} memories, I found {people_str.replace(' with ', '')} was there. {description}"
        else:
            summary = f"I found memories from your {event_name}, though I can't identify specific people. Here's what I see: {description}"
    else:
        summary = f"From your {event_name}{people_str}: {description}"

    # Add context if multiple relevant memories
    if len(memories) > 1:
        summary += f" I found {len(memories)} relevant memories from this event."

    return summary


def generate_answer_with_gemini(query: str, memories_context: str, memories: list, model_name: str = "gemini-pro") -> str:
    """
    Use Gemini to synthesize a natural answer from retrieved memories.

    Args:
        query: Original user query
        memories_context: Formatted context from retrieved memories
        model_name: Gemini model to use

    Returns:
        Natural language answer
    """
    print(f"🤖 Generating answer with {model_name}...\n")

    prompt = f"""You are ReMind, an AI memory companion helping someone recall their personal memories.
You have been given some memory clips that match their question. Your job is to synthesize a warm,
natural answer based on these memories.

User's Question: "{query}"

Retrieved Memories:
{memories_context}

Instructions:
1. Answer the user's question directly based on the memories provided
2. Be conversational and warm, as if helping someone remember
3. Mention specific details from the memories (what they ate, who was there, what happened)
4. If multiple memories are relevant, weave them together naturally
5. Keep it concise but informative (2-4 sentences)
6. If the memories don't fully answer the question, acknowledge what you can see and be honest about what's not shown

Answer:"""

    try:
        # Try different model names based on what's available
        model_names_to_try = [model_name, "models/gemini-pro", "models/gemini-1.5-pro", "models/gemini-1.5-flash"]

        last_error = None
        for model_to_try in model_names_to_try:
            try:
                model = genai.GenerativeModel(model_to_try)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=300,
                    )
                )
                return response.text
            except Exception as e:
                last_error = e
                continue

        # If all failed, raise the last error
        if last_error:
            raise last_error

    except Exception as e:
        print(f"❌ Error generating answer with Gemini: {e}")
        print("💡 Note: Update google-generativeai to >=0.8.0 and check your GEMINI_API_KEY")
        print("   Falling back to simple summary...\n")

        # Provide a simple rule-based fallback
        return generate_simple_summary(query, memories)


def retrieval_cycle(query: str, client: SnowflakeClient, top_k: int = 5, show_sources: bool = True):
    """
    Complete retrieval cycle: Search → Retrieve → Summarize

    Args:
        query: User's natural language question
        client: Connected SnowflakeClient
        top_k: Number of memories to retrieve
        show_sources: Whether to display source memories

    Returns:
        Tuple of (answer, memories)
    """
    # Step 1: Search for relevant memories
    memories = search_memories_by_query(query, client, top_k)

    if not memories:
        return "I couldn't find any memories matching your question.", []

    # Step 2: Format memories for Gemini
    memories_context = format_memories_for_gemini(memories)

    # Step 3: Generate natural language answer
    answer = generate_answer_with_gemini(query, memories_context, memories)

    # Display answer
    print("="*80)
    print("💭 ANSWER:")
    print("="*80)
    print(answer)
    print("="*80)

    # Optionally show source memories
    if show_sources:
        print("\n📚 SOURCE MEMORIES:")
        print("="*80)
        for idx, memory in enumerate(memories, 1):
            event_name, file_name, file_type, description, people, event_summary, file_url, similarity = memory

            # Format people array - filter out empty strings
            if people:
                people_list = [p.strip() for p in people if p and p.strip()]
                people_str = ", ".join(people_list) if people_list else "unknown"
            else:
                people_str = "unknown"

            print(f"\n🎬 Memory {idx} (Similarity: {similarity:.3f})")
            print(f"Event: {event_name}")
            print(f"File: {file_name}")
            print(f"People: {people_str}")
            print(f"Description: {description}")
            print(f"URL: {file_url}")

    return answer, memories


def interactive_retrieval():
    """Run interactive retrieval cycle."""
    print("🧠 ReMind - AI Memory Companion")
    print("="*80)
    print("Ask me about your memories, and I'll help you remember!")
    print("Examples:")
    print("  - What did we eat at Disney?")
    print("  - Tell me about the ski trip")
    print("  - Who was at the football game?")
    print("="*80)

    with SnowflakeClient() as client:
        while True:
            print("\n" + "="*80)
            query = input("💭 Your question (or 'quit' to exit): ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using ReMind. Take care!")
                break

            if not query:
                print("⚠️  Please enter a question")
                continue

            try:
                retrieval_cycle(query, client, top_k=5, show_sources=True)
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again with a different question.")


def test_retrieval():
    """Test retrieval cycle with sample queries."""
    print("🧠 ReMind - Testing Retrieval Cycle")
    print("="*80)

    test_queries = [
        "What did we eat at Disney?",
        "Tell me about the ski trip",
        "Who was at the football game?",
        "What happened during our day in college?",
        "Show me memories with Anna"
    ]

    with SnowflakeClient() as client:
        for query in test_queries:
            print(f"\n\n{'='*80}")
            print(f"TEST QUERY: {query}")
            print('='*80)

            retrieval_cycle(query, client, top_k=3, show_sources=True)

            input("\n⏸️  Press Enter to continue to next query...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='ReMind Retrieval Cycle')
    parser.add_argument('--test', action='store_true',
                       help='Run test queries')
    parser.add_argument('--query', type=str,
                       help='Single query to run (non-interactive)')
    parser.add_argument('--top-k', type=int, default=5,
                       help='Number of memories to retrieve (default: 5)')
    parser.add_argument('--no-sources', action='store_true',
                       help='Hide source memories in output')

    args = parser.parse_args()

    if args.test:
        test_retrieval()
    elif args.query:
        with SnowflakeClient() as client:
            retrieval_cycle(args.query, client,
                          top_k=args.top_k,
                          show_sources=not args.no_sources)
    else:
        interactive_retrieval()
