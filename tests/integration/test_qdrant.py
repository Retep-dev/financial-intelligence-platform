import uuid

import pytest

from db.qdrant.client import get_qdrant_client
from db.qdrant.collections import ensure_collection_exists, delete_collection, COLLECTION_NAME
from db.qdrant.queries import upsert_chunks, delete_document_chunks
from services.embeddings.client import get_embedding_dimensions


@pytest.fixture(scope="module", autouse=True)
def setup_collection():
    ensure_collection_exists()
    yield
    # Optional cleanup; uncomment to delete collection after tests
    # delete_collection()


def test_collection_exists():
    client = get_qdrant_client()
    collections = client.get_collections().collections
    names = [c.name for c in collections]
    assert COLLECTION_NAME in names


def test_upsert_and_delete_chunks():
    document_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())

    vector_size = get_embedding_dimensions()

    chunks = [{
        "chunk_id": chunk_id,
        "document_id": document_id,
        "chunk_index": 0,
        "text": "Revenue increased by 10%.",
        "embedding": [0.0] * vector_size,
        "file_name": "test.pdf",
        "source": "manual_upload"
    }]

    upsert_chunks(chunks)

    client = get_qdrant_client()
    result = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[chunk_id],
        with_payload=True
    )

    assert len(result) == 1
    assert result[0].payload["document_id"] == document_id
    assert result[0].payload["text"] == "Revenue increased by 10%."

    delete_document_chunks(document_id)

    result_after = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[chunk_id],
        with_payload=True
    )

    assert len(result_after) == 0
