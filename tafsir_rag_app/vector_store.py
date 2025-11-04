"""Vector store management using ChromaDB."""

from pathlib import Path
from typing import List, Optional, Union
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from tqdm import tqdm

from config import Config
from data_loader import TafsirDocument
from hadith_loader import HadithDocument


class TafsirVectorStore:
    """Manages the vector store for Islamic sources (Tafsir and Hadith)."""

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

    def add_documents(
        self,
        docs: List[Union[TafsirDocument, HadithDocument]],
        batch_size: int = 100
    ):
        """Add documents (Tafsir or Hadith) to the vector store.

        Args:
            docs: List of TafsirDocument or HadithDocument objects
            batch_size: Number of documents to process at once
        """
        if not docs:
            print("⚠️  No documents to add")
            return

        # Determine source type
        source_type = "documents"
        if docs and isinstance(docs[0], TafsirDocument):
            source_type = "tafsir documents"
        elif docs and isinstance(docs[0], HadithDocument):
            source_type = "hadith documents"

        print(f"\n📝 Adding {len(docs)} {source_type} to vector store...")

        # Convert to LangChain Document
        langchain_docs = []
        for doc in docs:
            langchain_doc = Document(
                page_content=doc.to_text(),
                metadata=doc.metadata,
            )
            langchain_docs.append(langchain_doc)

        # Add documents in batches
        total_docs = len(langchain_docs)
        for i in tqdm(range(0, total_docs, batch_size), desc=f"Adding {source_type}"):
            batch = langchain_docs[i:i + batch_size]
            self.vectorstore.add_documents(batch)

        print(f"✅ Successfully added {len(docs)} {source_type}")

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
    tafsir_edition_slugs: Optional[List[str]] = None,
    hadith_edition_slugs: Optional[List[str]] = None,
    enable_hadith: Optional[bool] = None,
    force_rebuild: bool = False,
) -> TafsirVectorStore:
    """Build or load the vector store with Tafsir and/or Hadith sources.

    Args:
        tafsir_edition_slugs: List of tafsir edition slugs to load
        hadith_edition_slugs: List of hadith edition slugs to load
        enable_hadith: Whether to load hadith (defaults to Config.ENABLE_HADITH)
        force_rebuild: Force rebuild even if store exists

    Returns:
        TafsirVectorStore instance
    """
    from data_loader import TafsirDataLoader
    from hadith_loader import HadithDataLoader

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

    all_documents = []

    # Load tafsir data
    if Config.TAFSIR_DATA_PATH.exists():
        tafsir_loader = TafsirDataLoader(Config.TAFSIR_DATA_PATH)
        tafsir_editions = tafsir_edition_slugs or Config.DEFAULT_EDITIONS

        print(f"\n📚 Loading Tafsir editions: {', '.join(tafsir_editions)}")
        tafsir_documents = tafsir_loader.load_multiple_editions(tafsir_editions)
        all_documents.extend(tafsir_documents)
    else:
        print("⚠️  Skipping Tafsir: data path not found")

    # Load hadith data (if enabled)
    if enable_hadith if enable_hadith is not None else Config.ENABLE_HADITH:
        hadith_loader = HadithDataLoader(Config.HADITH_CACHE_DIR)
        hadith_editions = hadith_edition_slugs or Config.DEFAULT_HADITH_EDITIONS

        print(f"\n📗 Loading Hadith editions: {', '.join(hadith_editions)}")
        max_hadiths = Config.MAX_HADITHS_PER_EDITION if Config.MAX_HADITHS_PER_EDITION > 0 else None

        hadith_documents = hadith_loader.load_multiple_editions(
            hadith_editions,
            max_hadiths_per_edition=max_hadiths
        )
        all_documents.extend(hadith_documents)

    if not all_documents:
        raise ValueError("No documents loaded. Check your data sources and configuration.")

    # Add all documents to vector store
    print(f"\n📊 Total documents to index: {len(all_documents)}")
    vector_store.add_documents(all_documents)

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
