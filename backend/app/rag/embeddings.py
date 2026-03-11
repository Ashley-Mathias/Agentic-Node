import logging

from app.config import get_openai_client

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate OpenAI embeddings for a batch of texts."""
    if not texts:
        return []

    client = get_openai_client()
    all_embeddings: list[list[float]] = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        all_embeddings.extend(item.embedding for item in response.data)

    logger.info("Generated %d embeddings (model=%s)", len(all_embeddings), EMBEDDING_MODEL)
    return all_embeddings


def get_single_embedding(text: str) -> list[float]:
    """Generate an embedding for a single text string."""
    return get_embeddings([text])[0]
