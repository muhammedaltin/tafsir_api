"""Configuration management for Tafsir RAG application."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # LLM Provider
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    # Tafsir Data
    TAFSIR_DATA_PATH = Path(os.getenv("TAFSIR_DATA_PATH", "../tafsir"))
    DEFAULT_EDITIONS = os.getenv(
        "DEFAULT_EDITIONS",
        "en-tafisr-ibn-kathir,en-al-jalalayn"
    ).split(",")

    # Hadith Data
    ENABLE_HADITH = os.getenv("ENABLE_HADITH", "true").lower() == "true"
    DEFAULT_HADITH_EDITIONS = os.getenv(
        "DEFAULT_HADITH_EDITIONS",
        "eng-bukhari,eng-muslim"
    ).split(",")
    MAX_HADITHS_PER_EDITION = int(os.getenv("MAX_HADITHS_PER_EDITION", "0"))  # 0 = all
    HADITH_CACHE_DIR = Path(os.getenv("HADITH_CACHE_DIR", "./hadith_cache"))

    # Vector Store
    VECTOR_STORE_PATH = Path(os.getenv("VECTOR_STORE_PATH", "./chroma_db"))
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "islamic_sources_collection")

    # RAG Configuration
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))

    @classmethod
    def validate(cls):
        """Validate configuration."""
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when using OpenAI provider. "
                "Please set it in .env file or use OLLAMA provider."
            )

        if not cls.TAFSIR_DATA_PATH.exists():
            print(
                f"⚠️  Warning: Tafsir data path not found: {cls.TAFSIR_DATA_PATH}. "
                "Tafsir sources will not be available."
            )

        return True


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
