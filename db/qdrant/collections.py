from qdrant_client.models import Distance, VectorParams

from db.qdrant.client import get_qdrant_client
from services.embeddings.client import get_embedding_dimensions

COLLECTION_NAME = "financial_chunks"


def get_vector_size() -> int:
    return get_embedding_dimensions()


def ensure_collection_exists() -> None:
    client = get_qdrant_client()

    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=get_vector_size(),
                distance=Distance.COSINE
            )
        )


def delete_collection() -> None:
    client = get_qdrant_client()
    client.delete_collection(collection_name=COLLECTION_NAME)
