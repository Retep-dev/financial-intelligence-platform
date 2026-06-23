import uuid

import pytest

from financial_intelligence_platform.db.qdrant.client import get_qdrant_client
from financial_intelligence_platform.db.qdrant.collections import (
    ensure_collection_exists,
    delete_collection,
    validate_collection,
    get_collection_info,
    COLLECTION_NAME
)
from financial_intelligence_platform.db.qdrant.queries import upsert_chunks, delete_document_chunks
from financial_intelligence_platform.db.qdrant.metrics import get_collection_stats, count_document_chunks
from financial_intelligence_platform.db.qdrant.snapshots import create_snapshot, list_snapshots, delete_snapshot
from financial_intelligence_platform.services.embeddings.client import get_embedding_dimensions


@pytest.fixture(scope="module", autouse=True)
def setup_collection():
    ensure_collection_exists()
    yield


def test_collection_has_expected_vector_size():
    info = get_collection_info()
    config = info["config"]["params"]["vectors"]
    assert config["size"] == get_embedding_dimensions()
    assert config["distance"] == "Cosine"


def test_validate_collection():
    assert validate_collection() is True


def test_payload_indexes_created():
    client = get_qdrant_client()
    info = get_collection_info()
    payload_schema = info["payload_schema"]

    assert "document_id" in payload_schema
    assert "source" in payload_schema
    assert "file_name" in payload_schema
    assert "chunk_index" in payload_schema
    assert "text" in payload_schema


def test_collection_stats():
    document_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())
    vector_size = get_embedding_dimensions()

    upsert_chunks([{
        "chunk_id": chunk_id,
        "document_id": document_id,
        "chunk_index": 0,
        "text": "Test chunk for metrics.",
        "embedding": [0.0] * vector_size,
        "file_name": "metrics_test.txt",
        "source": "manual_upload"
    }])

    stats = get_collection_stats()
    assert stats["collection"] == COLLECTION_NAME
    assert stats["points_count"] >= 1
    assert stats["vector_size"] == vector_size

    count = count_document_chunks(document_id)
    assert count == 1

    delete_document_chunks(document_id)


def test_snapshot_lifecycle():
    snapshot = create_snapshot()
    snapshot_name = snapshot.name

    snapshots = list_snapshots()
    names = [s.name for s in snapshots]
    assert snapshot_name in names

    deleted = delete_snapshot(snapshot_name)
    assert deleted is True
