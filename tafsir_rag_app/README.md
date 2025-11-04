# 📖 Islamic Sources RAG - AI-Powered Q&A System

An intelligent question-answering system that uses **Retrieval Augmented Generation (RAG)** to provide accurate answers about Islam based on:
- **📚 Tafsir** (Quranic interpretation) from renowned Islamic scholars
- **📗 Hadith** (Prophetic traditions) from authentic collections

## 🌟 Features

### Core Capabilities
- **🤖 AI-Powered Q&A**: Ask natural language questions about Islam, Quran, and Hadith
- **📚 Multiple Tafsir Sources**: 27+ editions from scholars like Ibn Kathir, Al-Jalalayn, Al-Qurtubi
- **📗 Hadith Collections**: 89+ editions including Sahih Bukhari, Sahih Muslim, and more
- **🔍 Semantic Search**: Find relevant content using vector similarity, not just keywords
- **🎯 Multi-Source Synthesis**: Combines insights from both Tafsir and Hadith
- **📊 Proper Citations**: Provides Surah/Ayah numbers and Hadith references
- **💬 Interactive CLI**: Easy-to-use command-line interface
- **🌐 Multiple Languages**: Arabic, English, Urdu, Bengali, Indonesian, Turkish, French, Russian

## 🏗️ Architecture

```
User Question → Intent Analysis → Vector Search → Context Retrieval → LLM Generation → Answer with Sources
```

### Components:

1. **Data Loaders**:
   - Tafsir: Loads from local JSON files
   - Hadith: Fetches from hadith-api CDN
2. **Embeddings**: Converts text to vector representations
3. **Vector Store**: ChromaDB storing both Tafsir and Hadith
4. **RAG Pipeline**: Retrieves relevant context and generates answers
5. **LLM Integration**: OpenAI GPT or Ollama for local inference

### Data Sources:

- **Tafsir**: 27 editions, 6 languages, 6000+ verses
- **Hadith**: 89 editions, 10 collections (Bukhari, Muslim, etc.), 9 languages

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (or Ollama for local LLM)
- Internet connection (for Hadith data)
- Tafsir data (optional, from parent directory)

### Installation

1. **Clone or navigate to the project directory**:
```bash
cd tafsir_rag_app
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### First Run

1. **Build the vector store index** (one-time setup):
```bash
python app.py --build-index
```

This will:
- Load tafsir data from default editions (if available)
- Fetch hadith from Sahih Bukhari & Muslim (via CDN)
- Generate embeddings for all content
- Store in local ChromaDB database
- Takes ~15-30 minutes for first time (downloads + embedding)

2. **Start asking questions**!
```bash
python app.py --interactive
```

## 📖 Usage

### Interactive Mode (Recommended)

```bash
python app.py --interactive
# or simply
python app.py
```

Then ask questions like:
- "What does the Quran say about patience?" (gets Tafsir)
- "What did the Prophet say about kindness?" (gets Hadith)
- "Explain the meaning of Al-Fatiha" (gets Tafsir)
- "How should I perform wudu?" (gets Hadith)
- "What is the importance of prayer?" (gets both Tafsir & Hadith)
- "Tell me about the story of Prophet Moses" (gets both)

### Single Question

```bash
python app.py --query "What does Islam teach about charity?"
```

### Simple Search (No LLM)

```bash
python app.py --search "patience" --top-k 5
```

### List Available Editions

```bash
python app.py --list-editions
```

### Build Index with Specific Sources

**Tafsir + Hadith (custom editions):**
```bash
python app.py --build-index \
  --tafsir-editions en-tafisr-ibn-kathir en-al-jalalayn \
  --hadith-editions eng-bukhari eng-muslim eng-abudawud
```

**Only Tafsir (no Hadith):**
```bash
python app.py --build-index --no-hadith \
  --tafsir-editions en-tafisr-ibn-kathir
```

**Only Hadith (no Tafsir):**
```bash
python app.py --build-index \
  --hadith-editions eng-bukhari eng-muslim
# (Tafsir will be skipped if data path not found)
```

**Force Rebuild:**
```bash
python app.py --build-index --force
```

## ⚙️ Configuration

Edit `.env` file to customize:

### LLM Provider Options

#### Option 1: OpenAI (Recommended - Best Quality)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

#### Option 2: Ollama (Free - Runs Locally)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

To use Ollama:
1. Install Ollama from https://ollama.ai
2. Pull models: `ollama pull llama3.2` and `ollama pull nomic-embed-text`
3. Uncomment Ollama section in requirements.txt: `pip install langchain-community`

### Data Configuration

```env
# Tafsir Data
TAFSIR_DATA_PATH=../tafsir
DEFAULT_EDITIONS=en-tafisr-ibn-kathir,en-al-jalalayn

# Hadith Data
ENABLE_HADITH=true
DEFAULT_HADITH_EDITIONS=eng-bukhari,eng-muslim
MAX_HADITHS_PER_EDITION=0  # 0 = load all, or set limit (e.g., 1000)
HADITH_CACHE_DIR=./hadith_cache

# Vector Store
VECTOR_STORE_PATH=./chroma_db
COLLECTION_NAME=islamic_sources_collection

# RAG Settings
TOP_K_RESULTS=5  # Number of sources to retrieve per query
```

**Hadith Settings Explained:**
- `ENABLE_HADITH=true`: Include hadith in searches
- `DEFAULT_HADITH_EDITIONS`: Which collections to load (comma-separated)
- `MAX_HADITHS_PER_EDITION=0`: Load all hadith (set to 1000-2000 for faster indexing)
- `HADITH_CACHE_DIR`: Where to cache downloaded hadith data

## 📚 Available Sources

### Tafsir Editions

**27 tafsir editions** in multiple languages:

### English (8 editions)
- `en-tafisr-ibn-kathir` - Tafsir Ibn Kathir (Abridged)
- `en-al-jalalayn` - Tafsir al-Jalalayn
- `en-tazkirul-quran` - Tazkirul Quran
- `en-maarif-ul-quran` - Maarif-ul-Quran
- And more...

### Arabic (8 editions)
- `ar-tafsir-ibn-kathir` - تفسير ابن كثير
- `ar-tafsir-al-tabari` - تفسير الطبري
- `ar-tafsir-al-qurtubi` - تفسير القرطبي
- And more...

### Other Languages
- Bengali (4 editions)
- Urdu (3 editions)
- Russian (1 edition)
- Kurdish (1 edition)

### Hadith Collections

**89 hadith editions** across **10 collections** in **9 languages**:

#### Major Collections (The Six Books)
- `eng-bukhari` - **Sahih al-Bukhari** (~7,500 hadith)
- `eng-muslim` - **Sahih Muslim** (~7,500 hadith)
- `eng-abudawud` - **Sunan Abu Dawud**
- `eng-tirmidhi` - **Jami At-Tirmidhi**
- `eng-ibnmajah` - **Sunan Ibn Majah**
- `eng-nasai` - **Sunan an-Nasai**

#### Additional Collections
- `eng-malik` - Muwatta Malik
- Forty Hadith an-Nawawi
- Forty Hadith Qudsi
- And more...

#### Other Languages
- Arabic: `ara-bukhari`, `ara-muslim`, etc. (with full diacritics)
- Urdu: `urd-bukhari`, `urd-muslim`, etc. (RTL support)
- Bengali, Indonesian, Turkish, Russian, French, Tamil

**Run `python app.py --list-editions` to see all available editions.**

**Note:** See [HADITH_INTEGRATION.md](HADITH_INTEGRATION.md) for detailed hadith documentation.

## 🧠 How RAG Works

### 1. **Indexing Phase** (Build Index)
```
Tafsir Text (local) → Embeddings → Vector Store
      +                                ↓
Hadith Text (CDN)  → Embeddings → Same Vector Store
```

### 2. **Query Phase** (Ask Question)
```
User Question → Embedding → Similarity Search (Tafsir + Hadith) → Top K Results
                                                                         ↓
                           User Question + Context → LLM → Answer + Citations
                                                              ↓
                                         FROM TAFSIR: [Surah X, Ayah Y...]
                                         FROM HADITH: [Bukhari 123, Muslim 456...]
```

### Why RAG?

- **Accuracy**: Answers are grounded in actual tafsir text
- **Attribution**: Always know which scholar/tafsir the answer comes from
- **Up-to-date**: Add new tafsir editions without retraining models
- **Transparency**: See the exact sources used to generate answers

## 🔧 Advanced Usage

### Python API

```python
from vector_store import build_vector_store
from rag_pipeline import TafsirRAGPipeline

# Build/load vector store
vector_store = build_vector_store()

# Create RAG pipeline
rag = TafsirRAGPipeline(vector_store)

# Ask a question
result = rag.query("What is the meaning of Bismillah?")

print(result['answer'])
for doc in result['sources']:
    print(f"Source: {doc.metadata['reference']}")
```

### Custom Editions

```python
from vector_store import build_vector_store

# Build index with specific editions
vector_store = build_vector_store(
    edition_slugs=['ar-tafsir-ibn-kathir', 'ar-tafsir-al-tabari'],
    force_rebuild=True
)
```

## 📊 Performance

- **Index Size**: ~500MB-1GB (depends on editions)
- **Query Time**: 2-5 seconds (including LLM generation)
- **Accuracy**: Based on authentic scholarly tafsir sources
- **Languages**: 6 languages supported

## 🐛 Troubleshooting

### Error: "OPENAI_API_KEY is required"
- Copy `.env.example` to `.env`
- Add your OpenAI API key
- Or switch to Ollama provider for free local inference

### Error: "Tafsir data path not found"
- Ensure the `tafsir` directory exists in the parent folder
- Or update `TAFSIR_DATA_PATH` in `.env`

### Slow indexing
- This is normal for first run (embedding 6000+ verses)
- Consider using fewer editions initially
- Embeddings are cached in ChromaDB for fast subsequent queries

### ChromaDB issues
- Delete `chroma_db` directory and rebuild: `python app.py --build-index --force`

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Add web interface (Streamlit/Gradio)
- Support for additional tafsir sources
- Multi-language query support
- Query optimization and caching
- Conversation history

## 📝 License

This project uses tafsir data from authenticated Islamic sources. Please respect the scholarship and use responsibly.

## 🙏 Acknowledgments

- Tafsir data sourced from Quran.com and Altafsir.com
- Built with LangChain, ChromaDB, and OpenAI
- Islamic scholarship from renowned scholars like Ibn Kathir, Al-Jalalayn, and others

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review configuration in `.env`
3. Ensure tafsir data is available
4. Open an issue on GitHub

---

**May this tool help in understanding the Quran better. Ameen.**
