#!/bin/bash

# Tafsir RAG Application Setup Script

set -e

echo "📖 Tafsir RAG Application Setup"
echo "================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# Check if Python 3.9+
required_version="3.9"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.9+ is required"
    echo "   Current version: $python_version"
    exit 1
fi

echo "✅ Python version OK"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install requirements
echo "📥 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup .env file
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "⚠️  IMPORTANT: You need to configure your .env file!"
    echo ""
    echo "For OpenAI (recommended):"
    echo "  1. Get API key from https://platform.openai.com/api-keys"
    echo "  2. Edit .env and set OPENAI_API_KEY=your_key_here"
    echo ""
    echo "For Ollama (free, local):"
    echo "  1. Install Ollama from https://ollama.ai"
    echo "  2. Run: ollama pull llama3.2"
    echo "  3. Run: ollama pull nomic-embed-text"
    echo "  4. Edit .env and set LLM_PROVIDER=ollama"
    echo ""
else
    echo "✅ .env file already exists"
fi
echo ""

# Check if tafsir data exists
echo "📚 Checking tafsir data..."
tafsir_path="../tafsir"
if [ -d "$tafsir_path" ]; then
    echo "✅ Tafsir data found at $tafsir_path"
else
    echo "⚠️  Warning: Tafsir data not found at $tafsir_path"
    echo "   Make sure to run the data scraper first or update TAFSIR_DATA_PATH in .env"
fi
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "✨ Setup Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your API key:"
echo "   nano .env  # or use your favorite editor"
echo ""
echo "2. Build the vector store index:"
echo "   python app.py --build-index"
echo ""
echo "3. Start asking questions:"
echo "   python app.py --interactive"
echo ""
echo "For more help:"
echo "   python app.py --help"
echo "   cat README.md"
echo ""
echo "═══════════════════════════════════════════════════════════"
