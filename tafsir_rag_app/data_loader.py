"""Data loader for Tafsir JSON files."""

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from tqdm import tqdm


@dataclass
class TafsirDocument:
    """Represents a single tafsir document (ayah interpretation)."""

    surah: int
    ayah: int
    text: str
    edition_name: str
    edition_slug: str
    author_name: str
    language: str

    @property
    def reference(self) -> str:
        """Return Quranic reference (e.g., 'Surah 1, Ayah 1')."""
        return f"Surah {self.surah}, Ayah {self.ayah}"

    @property
    def metadata(self) -> Dict:
        """Return metadata for vector store."""
        return {
            "surah": self.surah,
            "ayah": self.ayah,
            "edition": self.edition_slug,
            "edition_name": self.edition_name,
            "author": self.author_name,
            "language": self.language,
            "reference": self.reference,
        }

    def to_text(self) -> str:
        """Convert to text format for embedding."""
        return (
            f"Surah {self.surah}, Ayah {self.ayah}\n"
            f"Tafsir by {self.author_name} ({self.edition_name})\n\n"
            f"{self.text}"
        )


class TafsirDataLoader:
    """Loads tafsir data from JSON files."""

    def __init__(self, data_path: Path):
        """Initialize the data loader.

        Args:
            data_path: Path to the tafsir data directory
        """
        self.data_path = Path(data_path)
        self.editions_metadata: Dict = {}
        self._load_editions_metadata()

    def _load_editions_metadata(self):
        """Load editions metadata from editions.json."""
        editions_file = self.data_path / "editions.json"
        if editions_file.exists():
            with open(editions_file, "r", encoding="utf-8") as f:
                editions = json.load(f)
                # Create a lookup dictionary by slug
                self.editions_metadata = {
                    edition["slug"]: edition for edition in editions
                }
        else:
            print(f"⚠️  Warning: editions.json not found at {editions_file}")

    def load_edition(
        self,
        edition_slug: str,
        surahs: Optional[List[int]] = None
    ) -> List[TafsirDocument]:
        """Load all tafsir documents for a specific edition.

        Args:
            edition_slug: The edition identifier (e.g., 'en-tafisr-ibn-kathir')
            surahs: Optional list of surah numbers to load (default: all 114)

        Returns:
            List of TafsirDocument objects
        """
        documents = []
        edition_path = self.data_path / edition_slug

        if not edition_path.exists():
            print(f"⚠️  Warning: Edition path not found: {edition_path}")
            return documents

        # Get edition metadata
        edition_meta = self.editions_metadata.get(edition_slug, {})
        edition_name = edition_meta.get("name", edition_slug)
        author_name = edition_meta.get("author_name", "Unknown")
        language = edition_meta.get("language_name", "Unknown")

        # If no surahs specified, load all (1-114)
        if surahs is None:
            surahs = range(1, 115)

        print(f"📖 Loading {edition_name}...")

        for surah_num in tqdm(surahs, desc=f"Loading {edition_slug}"):
            surah_dir = edition_path / str(surah_num)

            if not surah_dir.exists():
                continue

            # Load individual ayah files
            for ayah_file in sorted(surah_dir.glob("*.json")):
                # Skip empty_ayahs.json
                if ayah_file.name == "empty_ayahs.json":
                    continue

                try:
                    with open(ayah_file, "r", encoding="utf-8") as f:
                        ayah_data = json.load(f)

                    # Skip empty text
                    if not ayah_data.get("text", "").strip():
                        continue

                    doc = TafsirDocument(
                        surah=ayah_data["surah"],
                        ayah=ayah_data["ayah"],
                        text=ayah_data["text"],
                        edition_name=edition_name,
                        edition_slug=edition_slug,
                        author_name=author_name,
                        language=language,
                    )
                    documents.append(doc)

                except (json.JSONDecodeError, KeyError) as e:
                    print(f"⚠️  Error loading {ayah_file}: {e}")
                    continue

        print(f"✅ Loaded {len(documents)} documents from {edition_name}")
        return documents

    def load_multiple_editions(
        self,
        edition_slugs: List[str],
        surahs: Optional[List[int]] = None
    ) -> List[TafsirDocument]:
        """Load tafsir documents from multiple editions.

        Args:
            edition_slugs: List of edition identifiers
            surahs: Optional list of surah numbers to load

        Returns:
            Combined list of TafsirDocument objects
        """
        all_documents = []

        for edition_slug in edition_slugs:
            documents = self.load_edition(edition_slug, surahs)
            all_documents.extend(documents)

        print(f"\n✅ Total documents loaded: {len(all_documents)}")
        return all_documents

    def get_available_editions(self) -> List[Dict]:
        """Get list of available editions.

        Returns:
            List of edition metadata dictionaries
        """
        editions = []
        for edition_dir in self.data_path.iterdir():
            if edition_dir.is_dir() and not edition_dir.name.startswith("."):
                edition_meta = self.editions_metadata.get(edition_dir.name, {})
                editions.append({
                    "slug": edition_dir.name,
                    "name": edition_meta.get("name", edition_dir.name),
                    "author": edition_meta.get("author_name", "Unknown"),
                    "language": edition_meta.get("language_name", "Unknown"),
                })
        return editions


def main():
    """Test the data loader."""
    from config import Config

    loader = TafsirDataLoader(Config.TAFSIR_DATA_PATH)

    # Show available editions
    print("\n📚 Available Editions:")
    for edition in loader.get_available_editions():
        print(f"  - {edition['slug']}: {edition['name']} ({edition['language']})")

    # Load a sample edition
    print("\n" + "=" * 60)
    docs = loader.load_edition("en-tafisr-ibn-kathir", surahs=[1])  # Load only Al-Fatiha

    if docs:
        print(f"\n📄 Sample Document:")
        print(f"Reference: {docs[0].reference}")
        print(f"Author: {docs[0].author_name}")
        print(f"Text: {docs[0].text[:200]}...")


if __name__ == "__main__":
    main()
