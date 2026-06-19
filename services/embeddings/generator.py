from typing import List, Dict

from core.config.settings import settings
from services.embeddings.client import get_embedding_client, get_embedding_model


def generate_embeddings(texts: List[str], input_type: str = "passage") -> List[List[float]]:
    """Generate embeddings for a list of texts using the configured provider."""
    if not texts:
        return []

    client = get_embedding_client()
    model = get_embedding_model()

    kwargs = {
        "input": texts,
        "model": model
    }

    # NVIDIA NIM models require input_type and encoding_format
    if settings.EMBEDDING_PROVIDER.lower() == "nvidia":
        kwargs["extra_body"] = {
            "input_type": input_type,
            "encoding_format": "float"
        }

    response = client.embeddings.create(**kwargs)

    return [item.embedding for item in response.data]


def generate_chunk_embeddings(chunks: List[Dict]) -> List[Dict]:
    """Generate embeddings for chunks and attach them to the chunk dicts."""
    if not chunks:
        return chunks

    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts, input_type="passage")

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding

    return chunks
