# Hadith Integration Guide

This document explains the Hadith integration in the Islamic Sources RAG application.

## Overview

The application now supports **both Tafsir (Quranic interpretation) and Hadith (Prophetic traditions)**, providing comprehensive answers to questions about Islam from multiple authentic sources.

## Features

### 📗 Hadith Collections

Access to **89 hadith editions** across **10 major collections**:

#### The Six Books (Kutub al-Sittah)
1. **Sahih al-Bukhari** - Most authentic collection
2. **Sahih Muslim** - Second most authentic
3. **Sunan Abu Dawud** - Focus on legal hadith
4. **Jami At-Tirmidhi** - With grading of authenticity
5. **Sunan Ibn Majah** - Legal and ritual matters
6. **Sunan an-Nasai** - Focused on jurisprudence

#### Additional Collections
7. **Muwatta Malik** - Earliest hadith compilation
8. **Forty Hadith an-Nawawi** - Essential hadith collection
9. **Forty Hadith Qudsi** - Sacred hadith
10. **Forty Hadith Shah Waliullah** - Spiritual guidance

### 🌍 Languages Supported

- **English** (primary for all collections)
- **Arabic** (original text with diacritics)
- **Urdu** (RTL support)
- **Bengali**
- **Indonesian**
- **Turkish**
- **Russian**
- **French**
- **Tamil**

## How It Works

### 1. Data Source

Hadith data is fetched from the [hadith-api](https://github.com/fawazahmed0/hadith-api) via CDN:
- Primary: `https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/`
- Fallback: GitHub raw
- Format: JSON (with minified .min.json option)

### 2. Data Structure

Each hadith contains:
```json
{
  "hadithnumber": 1,
  "arabicnumber": 1,
  "text": "Narrated 'Umar bin Al-Khattab: I heard Allah's Messenger (ﷺ) saying...",
  "grades": ["Sahih"],
  "reference": {
    "book": 1,
    "hadith": 1
  }
}
```

### 3. Metadata

Each hadith is enriched with:
- **Collection name** (e.g., "Sahih al-Bukhari")
- **Section/Chapter** (e.g., "Book of Revelation")
- **Hadith number** (both sequential and Arabic numbering)
- **Authenticity grade** (when available)
- **Language** and **Edition** information

### 4. RAG Integration

**Vector Embedding:**
- Each hadith is converted to text with metadata
- Embedded using OpenAI `text-embedding-3-small` or Ollama `nomic-embed-text`
- Stored in ChromaDB alongside tafsir documents

**Retrieval:**
- Semantic search finds relevant hadith based on question meaning
- Metadata filtering allows source-specific queries
- Returns top-k most relevant passages

**Generation:**
- LLM synthesizes answers from both Tafsir and Hadith
- Proper citation with collection name and hadith number
- Distinguishes between Tafsir and Hadith sources

## Usage

### Basic Setup

1. **Enable Hadith in configuration** (.env):
```env
ENABLE_HADITH=true
DEFAULT_HADITH_EDITIONS=eng-bukhari,eng-muslim
MAX_HADITHS_PER_EDITION=0  # 0 = load all
```

2. **Build index with Hadith**:
```bash
python app.py --build-index
```

This loads both default tafsir and hadith editions.

### Advanced Usage

#### Load Specific Hadith Collections
```bash
python app.py --build-index \
  --tafsir-editions en-tafisr-ibn-kathir \
  --hadith-editions eng-bukhari eng-muslim eng-abudawud
```

#### Load Only Hadith (No Tafsir)
```bash
python app.py --build-index \
  --hadith-editions eng-bukhari eng-muslim \
  --tafsir-editions none
```

Wait, that won't work. Let me provide the correct approach:

```bash
# In .env, set:
TAFSIR_DATA_PATH=/nonexistent  # Skip tafsir loading
ENABLE_HADITH=true
```

Then build:
```bash
python app.py --build-index
```

#### Disable Hadith
```bash
python app.py --build-index --no-hadith
```

Or in .env:
```env
ENABLE_HADITH=false
```

### Query Examples

#### Questions Best Answered by Hadith

```bash
python app.py --query "How did the Prophet perform wudu (ablution)?"
```

**Output:**
- Answer synthesized from Hadith descriptions
- Citations from Sahih Bukhari, Sahih Muslim
- Hadith numbers and sections provided

```bash
python app.py --query "What are the signs of the Day of Judgment?"
```

**Output:**
- Answer from both Hadith (specific narrations) and Tafsir (Quranic interpretation)
- Cross-referenced sources

#### Questions Answered by Both Sources

```bash
python app.py --query "What is the importance of Salah (prayer)?"
```

**Output:**
- Tafsir: Quranic verses about prayer
- Hadith: Prophetic teachings on prayer
- Comprehensive answer from both

## Technical Details

### Hadith Loader (`hadith_loader.py`)

**Key Features:**
- Fetches JSON from CDN with automatic fallback
- Caches downloaded data locally
- Parses section/chapter organization
- Handles multiple numbering systems
- Supports partial loading (limit hadiths per edition)

**HadithDocument Class:**
```python
@dataclass
class HadithDocument:
    hadith_number: int
    arabic_number: int
    text: str
    collection_name: str
    edition_slug: str
    language: str
    section_name: str
    section_number: int
    book_number: int
    grades: List[str]
```

### Vector Store Integration

**Unified Storage:**
- Both Tafsir and Hadith stored in same ChromaDB collection
- `source_type` metadata field distinguishes them
- Enables cross-source semantic search

**Filtering:**
```python
# Search only Hadith
vector_store.similarity_search(
    "prayer times",
    filter_metadata={"source_type": "hadith"}
)

# Search only Tafsir
vector_store.similarity_search(
    "verse meaning",
    filter_metadata={"source_type": "tafsir"}
)
```

### RAG Pipeline Enhancements

**Updated Prompt:**
- Instructs LLM to synthesize from both sources
- Provides citation guidelines for both types
- Handles scholarly differences

**Response Formatting:**
- Separates Tafsir and Hadith sources
- Different formatting for each type
- Displays authenticity grades for Hadith

## Performance Considerations

### Loading Time

**Full Collections:**
- Sahih Bukhari: ~7,500 hadith
- Sahih Muslim: ~7,500 hadith
- Combined: ~15,000 hadith
- First-time indexing: ~30-45 minutes

**Optimization:**
- Use `MAX_HADITHS_PER_EDITION` to limit
- Load fewer collections initially
- Embeddings are cached (subsequent queries fast)

Example - Load first 1000 hadith per collection:
```env
MAX_HADITHS_PER_EDITION=1000
```

### Storage

**Disk Space:**
- Each hadith ~500-1000 bytes
- 15,000 hadith ≈ 15 MB raw JSON
- With embeddings ≈ 200 MB in ChromaDB

### API Rate Limits

**CDN Access:**
- No strict rate limits (jsDelivr)
- Automatic retry with fallback
- Local caching prevents re-downloading

## Best Practices

### 1. Start Small
```bash
# Begin with most authentic collections
--hadith-editions eng-bukhari eng-muslim
```

### 2. Use Specific Questions
- ✅ Good: "How many times should I pray daily?"
- ✅ Good: "What did the Prophet say about honesty?"
- ❌ Too broad: "Tell me about Islam"

### 3. Verify Citations
- Always check the provided hadith references
- Cross-reference with original sources
- Note the authenticity grades

### 4. Combine Sources
- Ask questions that benefit from both Quran and Hadith
- Example: "What does Islam teach about charity?" (gets both)

## Troubleshooting

### Hadith Not Loading

**Check:**
1. `ENABLE_HADITH=true` in .env
2. Internet connection (for CDN access)
3. Firewall not blocking jsDelivr

**Solution:**
```bash
# Test hadith loader directly
python -c "from hadith_loader import HadithDataLoader; loader = HadithDataLoader(); docs = loader.load_edition('eng-bukhari', max_hadiths=10); print(f'Loaded {len(docs)} hadith')"
```

### Slow Indexing

**Cause:** Loading full collections

**Solution:**
```env
# Limit to first 2000 hadith per collection
MAX_HADITHS_PER_EDITION=2000
```

### No Hadith in Answers

**Check:**
1. Vector store was built with hadith enabled
2. Your question is relevant to hadith content
3. Rebuild index: `python app.py --build-index --force`

### Cache Issues

**Clear cache:**
```bash
rm -rf hadith_cache/
python app.py --build-index --force
```

## Example Queries

### Prophetic Guidance
```bash
python app.py -q "What did the Prophet say about kindness to neighbors?"
```

### Ritual Practices
```bash
python app.py -q "How should I perform Hajj?"
```

### Ethics and Morality
```bash
python app.py -q "What are the major sins in Islam?"
```

### Historical Context
```bash
python app.py -q "Why was Surah Al-Baqarah revealed?"
```

Gets both:
- Tafsir: Explanation of the Surah
- Hadith: Historical narrations about revelation

## API Reference

### Configuration

**Environment Variables:**
```env
ENABLE_HADITH=true|false
DEFAULT_HADITH_EDITIONS=eng-bukhari,eng-muslim
MAX_HADITHS_PER_EDITION=0
HADITH_CACHE_DIR=./hadith_cache
```

### CLI Arguments

```bash
--hadith-editions <slug1> <slug2>   # Specify hadith collections
--no-hadith                         # Disable hadith
--list-editions                     # Show all available editions
```

### Python API

```python
from hadith_loader import HadithDataLoader
from vector_store import build_vector_store

# Load specific hadith
loader = HadithDataLoader()
docs = loader.load_edition('eng-bukhari', max_hadiths=100)

# Build with hadith
vector_store = build_vector_store(
    hadith_edition_slugs=['eng-bukhari', 'eng-muslim'],
    enable_hadith=True
)
```

## Resources

- **Hadith API Repo:** https://github.com/fawazahmed0/hadith-api
- **Collections Info:** https://en.wikipedia.org/wiki/Hadith_collections
- **Authenticity Grading:** https://en.wikipedia.org/wiki/Hadith_terminology

## Future Enhancements

Potential improvements:
- [ ] Add more hadith collections
- [ ] Support hadith grading filters (only Sahih)
- [ ] Chain of narration (Isnad) analysis
- [ ] Hadith commentary (Sharh) integration
- [ ] Cross-reference with Quranic verses
- [ ] Timeline visualization of hadith

---

**Happy Learning! May this tool aid in understanding the Prophetic traditions.** 📗✨
