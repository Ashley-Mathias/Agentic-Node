# rag/ — ChromaDB collections, embeddings, and document ingestion.
import logging

import chromadb
from chromadb.utils import embedding_functions

from app.config import get_settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "documents"

_client = None
_collection = None


def get_chroma_client():
    """Return (and lazily initialise) the persistent ChromaDB client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        logger.info("ChromaDB client initialised at %s", settings.chroma_persist_dir)
    return _client


def get_collection():
    """Return (and lazily create) the default document collection."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        settings = get_settings()

        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name="text-embedding-3-small",
        )

        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=openai_ef,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB collection '%s' ready (%d existing documents)",
            COLLECTION_NAME,
            _collection.count(),
        )
    return _collection


def add_documents(chunks: list[str], metadata: list[dict], ids: list[str]) -> int:
    """Add document chunks to the vector store. Returns the number stored."""
    collection = get_collection()
    batch_size = 100
    total = 0

    for i in range(0, len(chunks), batch_size):
        collection.add(
            documents=chunks[i : i + batch_size],
            metadatas=metadata[i : i + batch_size],
            ids=ids[i : i + batch_size],
        )
        total += len(chunks[i : i + batch_size])

    logger.info("Stored %d chunks in vector store", total)
    return total


def search_documents(query: str, n_results: int = 5) -> list[dict]:
    """Return the top-*n_results* chunks most similar to *query*."""
    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
    )

    documents: list[dict] = []
    for i in range(len(results["documents"][0])):
        documents.append({
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else None,
        })

    logger.info("Vector search returned %d chunks", len(documents))
    return documents
