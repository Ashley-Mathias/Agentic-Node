import logging

from app.rag.vector_store import search_documents

logger = logging.getLogger(__name__)


def search_and_answer(question: str, n_results: int = 5) -> str:
    """Search the vector store and compile relevant context for the LLM.

    Returns a formatted string of the most relevant document chunks.
    The actual LLM answer generation is handled by the response_generator node.
    """
    results = search_documents(question, n_results=n_results)

    if not results:
        return "No relevant documents found in the knowledge base."

    context_parts: list[str] = []
    for i, doc in enumerate(results, 1):
        source = doc["metadata"].get("source", "Unknown")
        context_parts.append(f"[Source: {source} | Chunk {i}]\n{doc['content']}")

    context = "\n\n---\n\n".join(context_parts)
    logger.info("Built RAG context from %d chunks (%d chars)", len(results), len(context))
    return context
