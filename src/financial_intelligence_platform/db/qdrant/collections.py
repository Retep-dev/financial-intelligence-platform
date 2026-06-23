from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

from financial_intelligence_platform.db.qdrant.client import get_qdrant_client
from financial_intelligence_platform.services.embeddings.client import get_embedding_dimensions

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

    _ensure_payload_indexes(client)


def _ensure_payload_indexes(client) -> None:
    """Create payload indexes for efficient filtering and hybrid search."""
    index_configs = {
        "document_id": PayloadSchemaType.KEYWORD,
        "source": PayloadSchemaType.KEYWORD,
        "file_name": PayloadSchemaType.KEYWORD,
        "chunk_index": PayloadSchemaType.INTEGER,
        "text": PayloadSchemaType.TEXT,
    }

    for field_name, field_schema in index_configs.items():
        try:
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name=field_name,
                field_schema=field_schema
            )
        except Exception:
            # Index may already exist with a different type; skip
            pass


def delete_collection() -> None:
    client = get_qdrant_client()
    client.delete_collection(collection_name=COLLECTION_NAME)


def get_collection_info() -> dict:
    client = get_qdrant_client()
    return client.get_collection(collection_name=COLLECTION_NAME).model_dump()


def validate_collection() -> bool:
    """Validate that the existing collection has the expected vector size."""
    client = get_qdrant_client()

    try:
        info = client.get_collection(collection_name=COLLECTION_NAME)
    except Exception:
        return False

    actual_size = info.config.params.vectors.size
    expected_size = get_vector_size()

    return actual_size == expected_size
