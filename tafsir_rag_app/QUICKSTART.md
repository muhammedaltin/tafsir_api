# 🚀 Quick Start Guide

Get up and running with Tafsir RAG in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (or Ollama installed locally)
- Internet connection (for first-time setup)

## Step 1: Setup (2 minutes)

### Automatic Setup (Recommended)

```bash
cd tafsir_rag_app
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` configuration file

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp .env.example .env
```

## Step 2: Configure API Key (1 minute)

Edit `.env` file:

```bash
nano .env  # or use your favorite editor
```

**Option A: OpenAI (Easiest)**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```
Get your key from: https://platform.openai.com/api-keys

**Option B: Ollama (Free & Local)**
```env
LLM_PROVIDER=ollama
```
Then install Ollama and models:
```bash
# Install from https://ollama.ai
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Step 3: Build Index (5-10 minutes)

```bash
python app.py --build-index
```

This creates a searchable database from the tafsir data. Only needs to be done once!

**What's happening?**
- Loading tafsir texts from default editions
- Generating AI embeddings for semantic search
- Storing in local ChromaDB database

**Note**: This step takes time because it's processing 6000+ verses. Grab a coffee! ☕

## Step 4: Start Using! (30 seconds)

### Interactive Mode (Recommended for beginners)

```bash
python app.py --interactive
```

Then type questions like:
```
🤔 Your question: What does the Quran say about patience?

🤔 Your question: Explain the meaning of Surah Al-Fatiha

🤔 Your question: Tell me about Ayat al-Kursi
```

Type `exit` or `quit` to stop.

### Single Question Mode

```bash
python app.py --query "What is the importance of prayer in Islam?"
```

### Simple Search (Fast, no AI generation)

```bash
python app.py --search "charity" --top-k 5
```

## Example Session

```bash
$ python app.py --interactive

╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║          📖 TAFSIR RAG - Quranic Interpretation Assistant        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

🔄 Loading vector store...
✅ Vector store loaded (12450 documents)

🤖 Initializing AI assistant...
✅ Ready!

💬 Interactive Mode - Ask questions about the Quran
   Type 'quit' or 'exit' to stop


🤔 Your question: What does patience mean in Islam?

🤔 Analyzing question: What does patience mean in Islam?
🔍 Searching tafsir database...

======================================================================
📖 ANSWER
======================================================================
In Islam, patience (Sabr) is a fundamental virtue that encompasses...

[Full detailed answer based on authentic tafsir sources]

======================================================================
📚 SOURCES
======================================================================

1. Surah 2, Ayah 153
   📕 Tafsir Ibn Kathir (Abridged)
   ✍️  Ibn Kathir
   📄 [Relevant tafsir excerpt...]

2. Surah 103, Ayah 3
   📕 Tafsir al-Jalalayn
   ✍️  Al-Jalalayn
   📄 [Relevant tafsir excerpt...]

======================================================================


🤔 Your question: exit

👋 Goodbye! May peace be upon you.
```

## Common Issues & Solutions

### "OPENAI_API_KEY is required"
**Solution**: Edit `.env` and add your OpenAI API key, or switch to Ollama.

### "Tafsir data path not found"
**Solution**: Make sure you're running from the `tafsir_rag_app` directory and the parent directory contains the `tafsir` folder with data.

### Slow first query
**Solution**: This is normal! First query loads models into memory. Subsequent queries are much faster.

### ChromaDB errors
**Solution**: Delete `chroma_db` folder and rebuild:
```bash
rm -rf chroma_db
python app.py --build-index
```

## Tips for Best Results

1. **Ask clear, specific questions**
   - Good: "What does Surah Al-Fatiha teach about guidance?"
   - Okay: "Tell me about Al-Fatiha"

2. **Use natural language**
   - The AI understands conversational questions
   - No need for exact verse references (though you can use them)

3. **Explore different tafsir**
   - Different scholars offer different insights
   - Try building index with multiple editions

4. **Reference verification**
   - Always check the cited sources
   - The AI provides Surah and Ayah numbers for verification

## Advanced Usage

### Use specific tafsir editions
```bash
python app.py --build-index --editions en-tafisr-ibn-kathir ar-tafsir-ibn-kathir
```

### See all available editions
```bash
python app.py --list-editions
```

### Rebuild index with more/fewer verses
```bash
python app.py --build-index --force
```

## Next Steps

- Read the full [README.md](README.md) for advanced features
- Explore the code to customize behavior
- Try different tafsir editions
- Experiment with different question styles

## Getting Help

- Check [README.md](README.md) for detailed documentation
- Review configuration options in `.env`
- Make sure dependencies are installed: `pip install -r requirements.txt`

---

**Ready to explore the Quran with AI? Start asking questions!** 📖✨
