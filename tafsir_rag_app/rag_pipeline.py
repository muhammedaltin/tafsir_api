"""RAG pipeline for Tafsir question answering."""

from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from config import Config
from vector_store import TafsirVectorStore


class TafsirRAGPipeline:
    """RAG pipeline for answering questions about Quranic tafsir."""

    def __init__(self, vector_store: TafsirVectorStore):
        """Initialize the RAG pipeline.

        Args:
            vector_store: The vector store containing tafsir documents
        """
        self.vector_store = vector_store
        self.llm = self._initialize_llm()
        self.qa_chain = self._create_qa_chain()

    def _initialize_llm(self):
        """Initialize the language model."""
        if Config.LLM_PROVIDER == "openai":
            return ChatOpenAI(
                model=Config.OPENAI_MODEL,
                temperature=0.3,
                openai_api_key=Config.OPENAI_API_KEY,
            )
        elif Config.LLM_PROVIDER == "ollama":
            try:
                from langchain_community.llms import Ollama
                return Ollama(
                    model=Config.OLLAMA_MODEL,
                    base_url=Config.OLLAMA_BASE_URL,
                    temperature=0.3,
                )
            except ImportError:
                raise ImportError(
                    "Ollama support requires langchain-community. "
                    "Install with: pip install langchain-community"
                )
        else:
            raise ValueError(f"Unsupported LLM provider: {Config.LLM_PROVIDER}")

    def _create_qa_chain(self):
        """Create the QA chain with custom prompt."""

        prompt_template = """You are a knowledgeable Islamic scholar assistant specializing in Quranic tafsir (interpretation) and Hadith studies.

Your task is to answer questions about Islam based on the authentic sources provided below, which may include:
- Tafsir (Quranic interpretation) from renowned scholars
- Hadith (Prophetic traditions) from authentic collections

Context from Islamic Sources:
{context}

Question: {question}

Instructions:
1. Analyze the user's question to understand their intention
2. Use the sources provided in the context to formulate your answer
3. When citing Quranic verses, always include Surah and Ayah numbers
4. When citing Hadith, include the collection name and hadith number
5. If the sources mention different scholarly opinions, present them fairly
6. If the context doesn't contain relevant information, say so honestly
7. Synthesize information from both Tafsir and Hadith when both are available
8. Keep your answer clear, respectful, and informative
9. Use proper Islamic terminology and maintain scholarly tone

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        retriever = self.vector_store.as_retriever(k=Config.TOP_K_RESULTS)

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        return qa_chain

    def query(self, question: str) -> dict:
        """Query the RAG pipeline.

        Args:
            question: User's question

        Returns:
            Dictionary containing answer and source documents
        """
        print(f"\n🤔 Analyzing question: {question}")
        print("🔍 Searching tafsir database...")

        result = self.qa_chain.invoke({"query": question})

        return {
            "question": question,
            "answer": result["result"],
            "sources": result["source_documents"]
        }

    def format_response(self, result: dict) -> str:
        """Format the response for display.

        Args:
            result: Result dictionary from query()

        Returns:
            Formatted string
        """
        output = []
        output.append("\n" + "=" * 70)
        output.append("📖 ANSWER")
        output.append("=" * 70)
        output.append(result["answer"])
        output.append("\n" + "=" * 70)
        output.append("📚 SOURCES")
        output.append("=" * 70)

        # Separate sources by type
        tafsir_sources = []
        hadith_sources = []

        for doc in result["sources"]:
            if doc.metadata.get("source_type") == "hadith":
                hadith_sources.append(doc)
            else:
                tafsir_sources.append(doc)

        # Display Tafsir sources
        if tafsir_sources:
            output.append("\nFROM TAFSIR:")
            for i, doc in enumerate(tafsir_sources, 1):
                output.append(f"\n{i}. {doc.metadata['reference']}")
                output.append(f"   📕 {doc.metadata.get('edition_name', 'Unknown')}")
                output.append(f"   ✍️  {doc.metadata.get('author', 'Unknown')}")

                # Show excerpt
                content = doc.page_content
                if '\n\n' in content:
                    excerpt = content.split('\n\n', 1)[1]
                else:
                    excerpt = content

                if len(excerpt) > 300:
                    excerpt = excerpt[:300] + "..."

                output.append(f"   📄 {excerpt}")

        # Display Hadith sources
        if hadith_sources:
            output.append("\nFROM HADITH:")
            for i, doc in enumerate(hadith_sources, 1):
                output.append(f"\n{i}. {doc.metadata['reference']}")
                output.append(f"   📗 {doc.metadata.get('collection', 'Unknown Collection')}")

                section = doc.metadata.get('section', 'Unknown Section')
                output.append(f"   📖 Section: {section}")

                # Show grades if available
                grades = doc.metadata.get('grades', [])
                if grades:
                    output.append(f"   🔍 Grade: {', '.join(grades)}")

                # Show excerpt
                content = doc.page_content
                # Extract the hadith text (after the metadata lines)
                lines = content.split('\n')
                # Find where the actual hadith text starts (usually after empty line)
                text_start = 0
                for idx, line in enumerate(lines):
                    if line.strip() == "" and idx < len(lines) - 1:
                        text_start = idx + 1
                        break

                excerpt = '\n'.join(lines[text_start:]) if text_start < len(lines) else content

                if len(excerpt) > 350:
                    excerpt = excerpt[:350] + "..."

                output.append(f"   📄 {excerpt}")

        output.append("\n" + "=" * 70)
        return "\n".join(output)

    def search_similar(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar tafsir passages.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of similar documents
        """
        return self.vector_store.similarity_search(query, k=k)

    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """Search with relevance scores.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of (document, score) tuples
        """
        return self.vector_store.similarity_search_with_score(query, k=k)


class IntentAnalyzer:
    """Analyzes user intent to better understand questions."""

    def __init__(self, llm):
        """Initialize intent analyzer.

        Args:
            llm: Language model for intent analysis
        """
        self.llm = llm

    def analyze_intent(self, question: str) -> dict:
        """Analyze the intent behind a user's question.

        Args:
            question: User's question

        Returns:
            Dictionary with intent analysis
        """
        prompt = f"""Analyze the following question about the Quran or Islam and identify:
1. The main topic or theme
2. Whether it's asking about a specific verse, general concept, or practical guidance
3. Key terms that should be searched in tafsir

Question: {question}

Provide a brief analysis in JSON format:
{{
    "topic": "main topic",
    "query_type": "specific_verse|general_concept|practical_guidance|historical_context",
    "key_terms": ["term1", "term2"],
    "reformulated_query": "optimized search query"
}}
"""

        try:
            response = self.llm.invoke(prompt)
            # Parse the response (simplified)
            return {
                "original_question": question,
                "analysis": response.content if hasattr(response, 'content') else str(response)
            }
        except Exception as e:
            print(f"⚠️  Intent analysis failed: {e}")
            return {
                "original_question": question,
                "analysis": "Could not analyze intent"
            }


def main():
    """Test the RAG pipeline."""
    from vector_store import build_vector_store

    print("🚀 Initializing Tafsir RAG Pipeline...\n")

    # Build or load vector store
    vector_store = build_vector_store()

    # Create RAG pipeline
    rag = TafsirRAGPipeline(vector_store)

    # Test questions
    questions = [
        "What does the Quran say about patience?",
        "Explain the meaning of Al-Fatiha",
        "What is the significance of Ayat al-Kursi?",
    ]

    for question in questions:
        print("\n" + "#" * 70)
        print(f"QUESTION: {question}")
        print("#" * 70)

        result = rag.query(question)
        print(rag.format_response(result))

        # Wait for user input to continue
        input("\nPress Enter to continue to next question...")


if __name__ == "__main__":
    main()
