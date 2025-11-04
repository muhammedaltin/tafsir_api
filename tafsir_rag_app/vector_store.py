"""Vector store management using ChromaDB."""

from pathlib import Path
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from tqdm import tqdm

from config import Config
from data_loader import TafsirDocument


class TafsirVectorStore:
    """Manages the vector store for tafsir documents."""

    def __init__(
        self,
        persist_directory: Optional[Path] = None,
        collection_name: Optional[str] = None,
    ):
        """Initialize the vector store.

        Args:
            persist_directory: Directory to persist the vector store
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory or Config.VECTOR_STORE_PATH
        self.collection_name = collection_name or Config.COLLECTION_NAME

        # Initialize embeddings based on provider
        self.embeddings = self._initialize_embeddings()

        # Initialize ChromaDB
        self.vectorstore: Optional[Chroma] = None
        self._initialize_vectorstore()

    def _initialize_embeddings(self):
        """Initialize embedding model based on configuration."""
        if Config.LLM_PROVIDER == "openai":
            return OpenAIEmbeddings(
                model=Config.EMBEDDING_MODEL,
                openai_api_key=Config.OPENAI_API_KEY,
            )
        elif Config.LLM_PROVIDER == "ollama":
            try:
                from langchain_community.embeddings import OllamaEmbeddings
                return OllamaEmbeddings(
                    model=Config.OLLAMA_EMBEDDING_MODEL,
                    base_url=Config.OLLAMA_BASE_URL,
                )
            except ImportError:
                raise ImportError(
                    "Ollama embeddings require langchain-community. "
                    "Install with: pip install langchain-community"
                )
        else:
            raise ValueError(f"Unsupported LLM provider: {Config.LLM_PROVIDER}")

    def _initialize_vectorstore(self):
        """Initialize or load existing vector store."""
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory),
        )

    def add_documents(self, tafsir_docs: List[TafsirDocument], batch_size: int = 100):
        """Add tafsir documents to the vector store.

        Args:
            tafsir_docs: List of TafsirDocument objects
            batch_size: Number of documents to process at once
        """
        if not tafsir_docs:
            print("⚠️  No documents to add")
            return

        print(f"\n📝 Adding {len(tafsir_docs)} documents to vector store...")

        # Convert TafsirDocument to LangChain Document
        langchain_docs = []
        for doc in tafsir_docs:
            langchain_doc = Document(
                page_content=doc.to_text(),
                metadata=doc.metadata,
            )
            langchain_docs.append(langchain_doc)

        # Add documents in batches
        total_docs = len(langchain_docs)
        for i in tqdm(range(0, total_docs, batch_size), desc="Adding documents"):
            batch = langchain_docs[i:i + batch_size]
            self.vectorstore.add_documents(batch)

        print(f"✅ Successfully added {len(tafsir_docs)} documents")

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[dict] = None,
    ) -> List[Document]:
        """Search for similar documents.

        Args:
            query: The search query
            k: Number of results to return
            filter_metadata: Optional metadata filter (e.g., {'language': 'English'})

        Returns:
            List of similar documents
        """
        if filter_metadata:
            return self.vectorstore.similarity_search(
                query,
                k=k,
                filter=filter_metadata,
            )
        return self.vectorstore.similarity_search(query, k=k)

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[dict] = None,
    ) -> List[tuple[Document, float]]:
        """Search for similar documents with relevance scores.

        Args:
            query: The search query
            k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of (document, score) tuples
        """
        if filter_metadata:
            return self.vectorstore.similarity_search_with_score(
                query,
                k=k,
                filter=filter_metadata,
            )
        return self.vectorstore.similarity_search_with_score(query, k=k)

    def as_retriever(self, k: int = 5):
        """Return a retriever interface for RAG.

        Args:
            k: Number of documents to retrieve

        Returns:
            LangChain retriever
        """
        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            return self.vectorstore._collection.count()
        except Exception:
            return 0

    def delete_collection(self):
        """Delete the entire collection."""
        print(f"🗑️  Deleting collection: {self.collection_name}")
        try:
            client = chromadb.PersistentClient(path=str(self.persist_directory))
            client.delete_collection(name=self.collection_name)
            print("✅ Collection deleted")
        except Exception as e:
            print(f"⚠️  Error deleting collection: {e}")

    def collection_exists(self) -> bool:
        """Check if the collection exists and has documents."""
        return self.get_collection_count() > 0


def build_vector_store(
    edition_slugs: Optional[List[str]] = None,
    force_rebuild: bool = False,
) -> TafsirVectorStore:
    """Build or load the vector store.

    Args:
        edition_slugs: List of edition slugs to load
        force_rebuild: Force rebuild even if store exists

    Returns:
        TafsirVectorStore instance
    """
    from data_loader import TafsirDataLoader

    vector_store = TafsirVectorStore()

    # Check if vector store already exists
    if vector_store.collection_exists() and not force_rebuild:
        count = vector_store.get_collection_count()
        print(f"✅ Vector store already exists with {count} documents")
        print("   Use force_rebuild=True to rebuild")
        return vector_store

    # Delete existing collection if force rebuild
    if force_rebuild and vector_store.collection_exists():
        vector_store.delete_collection()
        vector_store = TafsirVectorStore()  # Reinitialize

    # Load tafsir data
    loader = TafsirDataLoader(Config.TAFSIR_DATA_PATH)
    editions = edition_slugs or Config.DEFAULT_EDITIONS

    print(f"\n📚 Loading editions: {', '.join(editions)}")
    documents = loader.load_multiple_editions(editions)

    if not documents:
        raise ValueError("No documents loaded. Check your data path and editions.")

    # Add documents to vector store
    vector_store.add_documents(documents)

    return vector_store


def main():
    """Test the vector store."""
    print("🚀 Building Vector Store...\n")

    # Build vector store
    vector_store = build_vector_store(force_rebuild=False)

    # Test search
    print("\n" + "=" * 60)
    print("🔍 Testing Search...")

    query = "What does Islam say about patience?"
    print(f"\nQuery: {query}")

    results = vector_store.similarity_search_with_score(query, k=3)

    print(f"\n📊 Top {len(results)} Results:\n")
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. Score: {score:.4f}")
        print(f"   Reference: {doc.metadata['reference']}")
        print(f"   Edition: {doc.metadata['edition_name']}")
        print(f"   Text: {doc.page_content[:200]}...")
        print()


if __name__ == "__main__":
    main()
