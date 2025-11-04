"""Data loader for Hadith from hadith-api."""

import json
import requests
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from tqdm import tqdm
import time


@dataclass
class HadithDocument:
    """Represents a single hadith document."""

    hadith_number: int
    arabic_number: int
    text: str
    collection_name: str
    edition_slug: str
    language: str
    section_name: Optional[str] = None
    section_number: Optional[int] = None
    book_number: Optional[int] = None
    grades: Optional[List] = None

    @property
    def reference(self) -> str:
        """Return hadith reference (e.g., 'Sahih Bukhari 1')."""
        return f"{self.collection_name} {self.hadith_number}"

    @property
    def full_reference(self) -> str:
        """Return full hadith reference with section."""
        if self.section_name:
            return f"{self.collection_name}, {self.section_name}, Hadith {self.hadith_number}"
        return self.reference

    @property
    def metadata(self) -> Dict:
        """Return metadata for vector store."""
        return {
            "hadith_number": self.hadith_number,
            "arabic_number": self.arabic_number,
            "collection": self.collection_name,
            "edition": self.edition_slug,
            "language": self.language,
            "section": self.section_name or "Unknown",
            "section_number": self.section_number,
            "book_number": self.book_number,
            "reference": self.reference,
            "full_reference": self.full_reference,
            "source_type": "hadith",  # Important: distinguish from tafsir
            "grades": self.grades or [],
        }

    def to_text(self) -> str:
        """Convert to text format for embedding."""
        parts = [
            f"{self.full_reference}",
            f"Collection: {self.collection_name} ({self.language})",
        ]

        if self.grades:
            parts.append(f"Grade: {', '.join(self.grades)}")

        parts.append("")  # Empty line before text
        parts.append(self.text)

        return "\n".join(parts)


class HadithDataLoader:
    """Loads hadith data from hadith-api CDN."""

    BASE_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1"
    FALLBACK_URL = "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1"

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the hadith loader.

        Args:
            cache_dir: Optional directory to cache downloaded data
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./hadith_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.editions_metadata: Dict = {}
        self._load_editions_metadata()

    def _fetch_json(self, endpoint: str, use_minified: bool = True) -> Dict:
        """Fetch JSON from API with fallback mechanism.

        Args:
            endpoint: API endpoint (e.g., 'editions/eng-bukhari/1')
            use_minified: Try minified version first

        Returns:
            JSON data as dictionary
        """
        extensions = [".min.json", ".json"] if use_minified else [".json", ".min.json"]
        urls = [self.BASE_URL, self.FALLBACK_URL]

        for ext in extensions:
            for base_url in urls:
                url = f"{base_url}/{endpoint}{ext}"
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        return response.json()
                except Exception as e:
                    continue

        raise Exception(f"Failed to fetch {endpoint} from all sources")

    def _load_editions_metadata(self):
        """Load editions metadata from API."""
        try:
            data = self._fetch_json("editions")
            # Create lookup dictionary by edition name
            for edition in data:
                self.editions_metadata[edition["name"]] = edition
            print(f"✅ Loaded {len(self.editions_metadata)} hadith editions metadata")
        except Exception as e:
            print(f"⚠️  Warning: Could not load editions metadata: {e}")

    def load_edition(
        self,
        edition_slug: str,
        max_hadiths: Optional[int] = None,
        sections: Optional[List[int]] = None,
    ) -> List[HadithDocument]:
        """Load all hadiths for a specific edition.

        Args:
            edition_slug: The edition identifier (e.g., 'eng-bukhari')
            max_hadiths: Optional limit on number of hadiths to load
            sections: Optional list of section numbers to load

        Returns:
            List of HadithDocument objects
        """
        documents = []

        try:
            print(f"\n📗 Loading {edition_slug}...")

            # Fetch the complete edition data
            edition_data = self._fetch_json(f"editions/{edition_slug}")

            metadata = edition_data.get("metadata", {})
            collection_name = metadata.get("name", edition_slug)
            section_map = metadata.get("section", {})
            hadiths_data = edition_data.get("hadiths", [])

            # Get language from edition slug
            language = self._get_language_from_slug(edition_slug)

            print(f"   Collection: {collection_name}")
            print(f"   Total hadiths: {len(hadiths_data)}")

            # Filter by sections if specified
            if sections:
                section_details = metadata.get("section_detail", {})
                filtered_hadiths = []
                for section_num in sections:
                    detail = section_details.get(str(section_num), {})
                    first = detail.get("hadithnumber_first", 0)
                    last = detail.get("hadithnumber_last", 0)
                    if first and last:
                        filtered_hadiths.extend([
                            h for h in hadiths_data
                            if first <= h.get("hadithnumber", 0) <= last
                        ])
                hadiths_data = filtered_hadiths

            # Limit number of hadiths if specified
            if max_hadiths:
                hadiths_data = hadiths_data[:max_hadiths]

            # Process each hadith
            for hadith in tqdm(hadiths_data, desc=f"Processing {edition_slug}"):
                hadith_num = hadith.get("hadithnumber")

                if not hadith_num or not hadith.get("text", "").strip():
                    continue

                # Find section for this hadith
                section_name = None
                section_number = None
                for sec_num, sec_name in section_map.items():
                    sec_detail = metadata.get("section_detail", {}).get(str(sec_num), {})
                    first = sec_detail.get("hadithnumber_first", 0)
                    last = sec_detail.get("hadithnumber_last", 0)
                    if first <= hadith_num <= last:
                        section_name = sec_name
                        section_number = int(sec_num)
                        break

                doc = HadithDocument(
                    hadith_number=hadith_num,
                    arabic_number=hadith.get("arabicnumber", hadith_num),
                    text=hadith.get("text", ""),
                    collection_name=collection_name,
                    edition_slug=edition_slug,
                    language=language,
                    section_name=section_name,
                    section_number=section_number,
                    book_number=hadith.get("reference", {}).get("book"),
                    grades=hadith.get("grades", []),
                )
                documents.append(doc)

            print(f"✅ Loaded {len(documents)} hadiths from {collection_name}")

        except Exception as e:
            print(f"❌ Error loading {edition_slug}: {e}")

        return documents

    def load_multiple_editions(
        self,
        edition_slugs: List[str],
        max_hadiths_per_edition: Optional[int] = None,
    ) -> List[HadithDocument]:
        """Load hadiths from multiple editions.

        Args:
            edition_slugs: List of edition identifiers
            max_hadiths_per_edition: Optional limit per edition

        Returns:
            Combined list of HadithDocument objects
        """
        all_documents = []

        for edition_slug in edition_slugs:
            documents = self.load_edition(edition_slug, max_hadiths=max_hadiths_per_edition)
            all_documents.extend(documents)
            time.sleep(0.5)  # Be nice to the CDN

        print(f"\n✅ Total hadith documents loaded: {len(all_documents)}")
        return all_documents

    def get_available_editions(self) -> List[Dict]:
        """Get list of available editions.

        Returns:
            List of edition metadata dictionaries
        """
        editions = []
        for edition_name, edition_meta in self.editions_metadata.items():
            editions.append({
                "slug": edition_meta.get("name"),
                "name": edition_name,
                "language": self._get_language_from_slug(edition_meta.get("name", "")),
            })
        return editions

    def _get_language_from_slug(self, slug: str) -> str:
        """Extract language from edition slug.

        Args:
            slug: Edition slug (e.g., 'eng-bukhari')

        Returns:
            Language name
        """
        lang_map = {
            "ara": "Arabic",
            "eng": "English",
            "urd": "Urdu",
            "ben": "Bengali",
            "ind": "Indonesian",
            "tur": "Turkish",
            "rus": "Russian",
            "fra": "French",
            "tam": "Tamil",
        }

        for prefix, language in lang_map.items():
            if slug.startswith(prefix):
                return language

        return "Unknown"


def main():
    """Test the hadith loader."""
    loader = HadithDataLoader()

    # Show available editions
    print("\n📚 Sample Available Editions:")
    editions = list(loader.editions_metadata.keys())[:10]
    for edition in editions:
        print(f"  - {edition}")

    # Load a sample edition
    print("\n" + "=" * 60)
    docs = loader.load_edition("eng-bukhari", max_hadiths=10)

    if docs:
        print(f"\n📄 Sample Hadith Document:")
        print(f"Reference: {docs[0].full_reference}")
        print(f"Section: {docs[0].section_name}")
        print(f"Text: {docs[0].text[:200]}...")
        print(f"\nFormatted for embedding:")
        print(docs[0].to_text()[:300] + "...")


if __name__ == "__main__":
    main()
