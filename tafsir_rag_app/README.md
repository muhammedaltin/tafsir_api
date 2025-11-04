# 📖 Tafsir RAG - Quranic Interpretation Assistant

An intelligent question-answering system that uses **Retrieval Augmented Generation (RAG)** to provide accurate answers about the Quran based on authentic tafsir (interpretations) from Islamic scholars.

## 🌟 Features

- **🤖 AI-Powered Q&A**: Ask natural language questions about the Quran
- **📚 Multiple Tafsir Sources**: Access interpretations from renowned scholars (Ibn Kathir, Al-Jalalayn, etc.)
- **🔍 Semantic Search**: Find relevant verses and interpretations using vector similarity
- **🎯 Intent Analysis**: Understands your question's context and intention
- **📊 Source Citations**: Always provides Surah and Ayah references
- **💬 Interactive CLI**: Easy-to-use command-line interface
- **🌐 Multiple Languages**: Support for Arabic, English, Urdu, Bengali, and more

## 🏗️ Architecture

```
User Question → Intent Analysis → Vector Search → Context Retrieval → LLM Generation → Answer with Sources
```

### Components:

1. **Data Loader**: Loads tafsir JSON files from the API
2. **Embeddings**: Converts text to vector representations
3. **Vector Store**: ChromaDB for efficient semantic search
4. **RAG Pipeline**: Retrieves relevant context and generates answers
5. **LLM Integration**: OpenAI GPT or Ollama for local inference

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (or Ollama for local LLM)
- Tafsir data (from parent directory)

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
- Load tafsir data from the default editions
- Generate embeddings for ~6000+ verses
- Store in local ChromaDB database
- Takes ~5-10 minutes depending on your API rate limits

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
- "What does the Quran say about patience?"
- "Explain the meaning of Al-Fatiha"
- "What is the significance of Ayat al-Kursi?"
- "Tell me about the story of Prophet Moses"

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

### Build Index with Specific Editions

```bash
python app.py --build-index --editions en-tafisr-ibn-kathir en-al-jalalayn ar-tafsir-ibn-kathir
```

### Force Rebuild Index

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
# Path to tafsir data directory
TAFSIR_DATA_PATH=../tafsir

# Default editions to load (comma-separated)
DEFAULT_EDITIONS=en-tafisr-ibn-kathir,en-al-jalalayn

# Vector store location
VECTOR_STORE_PATH=./chroma_db

# Number of results to retrieve
TOP_K_RESULTS=5
```

## 📚 Available Tafsir Editions

The application includes **27 tafsir editions** in multiple languages:

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

Run `python app.py --list-editions` to see all available editions.

## 🧠 How RAG Works

### 1. **Indexing Phase** (Build Index)
```
Tafsir Text → Chunking → Embeddings → Vector Store
```

### 2. **Query Phase** (Ask Question)
```
User Question → Embedding → Similarity Search → Top K Results → Context
                                                                    ↓
User Question + Context → LLM → Synthesized Answer + Citations
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
