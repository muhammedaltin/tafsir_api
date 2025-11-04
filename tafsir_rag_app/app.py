#!/usr/bin/env python3
"""
Tafsir RAG Application - Interactive CLI for Quranic Tafsir Q&A

This application uses Retrieval Augmented Generation (RAG) to answer questions
about the Quran based on authentic tafsir (interpretations) from Islamic scholars.
"""

import argparse
import sys
from pathlib import Path

from config import Config
from vector_store import build_vector_store, TafsirVectorStore
from rag_pipeline import TafsirRAGPipeline
from data_loader import TafsirDataLoader


def print_banner():
    """Print application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║          📖 TAFSIR RAG - Quranic Interpretation Assistant        ║
║                                                                   ║
║     Ask questions about the Quran and receive answers based      ║
║          on authentic tafsir from Islamic scholars               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def list_editions():
    """List available tafsir editions."""
    loader = TafsirDataLoader(Config.TAFSIR_DATA_PATH)
    editions = loader.get_available_editions()

    print("\n📚 Available Tafsir Editions:\n")
    print(f"{'Slug':<30} {'Name':<40} {'Language':<15}")
    print("=" * 90)

    for edition in editions:
        print(f"{edition['slug']:<30} {edition['name']:<40} {edition['language']:<15}")

    print(f"\n✅ Total: {len(editions)} editions available")


def build_index(editions: list, force: bool):
    """Build the vector store index.

    Args:
        editions: List of edition slugs to index
        force: Force rebuild if index exists
    """
    print("\n🔨 Building Vector Store Index...\n")

    if not editions:
        editions = Config.DEFAULT_EDITIONS
        print(f"📚 Using default editions: {', '.join(editions)}\n")

    try:
        vector_store = build_vector_store(
            edition_slugs=editions,
            force_rebuild=force
        )

        count = vector_store.get_collection_count()
        print(f"\n✅ Vector store ready with {count} documents")
        print(f"📁 Stored in: {Config.VECTOR_STORE_PATH}")

    except Exception as e:
        print(f"\n❌ Error building vector store: {e}")
        sys.exit(1)


def search_mode(vector_store: TafsirVectorStore, query: str, top_k: int):
    """Simple search mode without LLM.

    Args:
        vector_store: The vector store to search
        query: Search query
        top_k: Number of results to return
    """
    print(f"\n🔍 Searching for: {query}\n")

    results = vector_store.similarity_search_with_score(query, k=top_k)

    print(f"📊 Top {len(results)} Results:\n")
    print("=" * 70)

    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. Relevance Score: {score:.4f}")
        print(f"   📍 {doc.metadata['reference']}")
        print(f"   📕 {doc.metadata['edition_name']}")
        print(f"   ✍️  {doc.metadata['author']}")

        # Extract and display content
        content = doc.page_content
        if '\n\n' in content:
            excerpt = content.split('\n\n', 1)[1]
        else:
            excerpt = content

        if len(excerpt) > 400:
            excerpt = excerpt[:400] + "..."

        print(f"   📄 {excerpt}")
        print("-" * 70)


def interactive_mode(rag_pipeline: TafsirRAGPipeline):
    """Interactive question-answering mode.

    Args:
        rag_pipeline: The RAG pipeline
    """
    print("\n💬 Interactive Mode - Ask questions about the Quran")
    print("   Type 'quit' or 'exit' to stop\n")

    while True:
        try:
            question = input("\n🤔 Your question: ").strip()

            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! May peace be upon you.")
                break

            # Query the RAG pipeline
            result = rag_pipeline.query(question)

            # Display formatted response
            print(rag_pipeline.format_response(result))

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! May peace be upon you.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


def single_query_mode(rag_pipeline: TafsirRAGPipeline, question: str):
    """Single question mode.

    Args:
        rag_pipeline: The RAG pipeline
        question: The question to ask
    """
    print(f"\n🤔 Question: {question}")

    result = rag_pipeline.query(question)
    print(rag_pipeline.format_response(result))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Tafsir RAG - Quranic Interpretation Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available tafsir editions
  python app.py --list-editions

  # Build vector store index with default editions
  python app.py --build-index

  # Build index with specific editions
  python app.py --build-index --editions en-tafisr-ibn-kathir en-al-jalalayn

  # Force rebuild index
  python app.py --build-index --force

  # Interactive mode
  python app.py --interactive

  # Ask a single question
  python app.py --query "What does the Quran say about patience?"

  # Simple search without LLM
  python app.py --search "patience" --top-k 5
        """
    )

    parser.add_argument(
        "--list-editions",
        action="store_true",
        help="List all available tafsir editions"
    )

    parser.add_argument(
        "--build-index",
        action="store_true",
        help="Build the vector store index"
    )

    parser.add_argument(
        "--editions",
        nargs="+",
        help="Tafsir editions to use (space-separated slugs)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force rebuild of vector store"
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive Q&A mode"
    )

    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Ask a single question"
    )

    parser.add_argument(
        "--search",
        "-s",
        type=str,
        help="Simple search mode (no LLM generation)"
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n💡 Tip: Copy .env.example to .env and configure your settings")
        sys.exit(1)

    # Handle commands
    if args.list_editions:
        list_editions()
        return

    if args.build_index:
        build_index(args.editions, args.force)
        return

    # For other modes, we need the vector store
    try:
        print("🔄 Loading vector store...")
        vector_store = build_vector_store(edition_slugs=args.editions)
        print(f"✅ Vector store loaded ({vector_store.get_collection_count()} documents)\n")
    except Exception as e:
        print(f"\n❌ Error loading vector store: {e}")
        print("\n💡 Tip: Run with --build-index first to create the index")
        sys.exit(1)

    # Simple search mode
    if args.search:
        search_mode(vector_store, args.search, args.top_k)
        return

    # Create RAG pipeline for query modes
    print("🤖 Initializing AI assistant...")
    rag_pipeline = TafsirRAGPipeline(vector_store)
    print("✅ Ready!\n")

    # Single query mode
    if args.query:
        single_query_mode(rag_pipeline, args.query)
        return

    # Interactive mode (default if nothing specified)
    if args.interactive or len(sys.argv) == 1:
        interactive_mode(rag_pipeline)
        return

    # If no mode specified, show help
    parser.print_help()


if __name__ == "__main__":
    main()
