import os
import tempfile
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from financial_intelligence_platform.main import app
from financial_intelligence_platform.db.postgres.session import SessionLocal
from financial_intelligence_platform.db.postgres.models.chunk import Chunk
from financial_intelligence_platform.db.postgres.models.document import Document
from financial_intelligence_platform.db.qdrant.client import get_qdrant_client
from financial_intelligence_platform.db.qdrant.collections import COLLECTION_NAME
from financial_intelligence_platform.db.qdrant.queries import upsert_chunks
from financial_intelligence_platform.services.ingestion.service import create_document_record
from financial_intelligence_platform.services.embeddings.client import get_embedding_dimensions
from financial_intelligence_platform.services.retrieval.dense_search import dense_search
from financial_intelligence_platform.services.retrieval.bm25_search import bm25_search
from financial_intelligence_platform.services.retrieval.hybrid_search import hybrid_search


client = TestClient(app)


def test_dense_search():
    document_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())
    vector_size = get_embedding_dimensions()

    chunks = [{
        "chunk_id": chunk_id,
        "document_id": document_id,
        "chunk_index": 0,
        "text": "Revenue increased by 12% year over year to USD 4.2 billion.",
        "embedding": [1.0] + [0.0] * (vector_size - 1),
        "file_name": "earnings.txt",
        "source": "manual_upload"
    }]

    upsert_chunks(chunks)

    try:
        with patch("financial_intelligence_platform.services.retrieval.dense_search.generate_embeddings") as mock_embed:
            mock_embed.return_value = [[1.0] + [0.0] * (vector_size - 1)]

            results = dense_search("Revenue increased")
            assert len(results) >= 1
            assert results[0]["chunk_id"] == chunk_id
    finally:
        qdrant = get_qdrant_client()
        qdrant.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[chunk_id]
        )


def test_bm25_search():
    document = create_document_record(
        original_filename="bm25_test.txt",
        file_path="/tmp/bm25_test.txt"
    )

    db = SessionLocal()
    try:
        chunk = Chunk(
            document_id=document.id,
            chunk_index=0,
            chunk_text="Revenue increased significantly in the fourth quarter.",
            embedding_id=str(uuid.uuid4()),
            status="embedded"
        )
        db.add(chunk)
        db.commit()

        results = bm25_search(db=db, query="Revenue fourth quarter")
        assert len(results) >= 1
        assert document.id in [r["payload"]["document_id"] for r in results]
    finally:
        db.query(Chunk).filter(Chunk.document_id == document.id).delete()
        db.query(Document).filter(Document.id == document.id).delete()
        db.commit()
        db.close()


def test_hybrid_search():
    document = create_document_record(
        original_filename="hybrid_test.txt",
        file_path="/tmp/hybrid_test.txt"
    )

    chunk_id = str(uuid.uuid4())
    vector_size = get_embedding_dimensions()

    db = SessionLocal()
    try:
        chunk = Chunk(
            document_id=document.id,
            chunk_index=0,
            chunk_text="Operating margin expanded to 18% in fiscal year 2024.",
            embedding_id=chunk_id,
            status="embedded"
        )
        db.add(chunk)
        db.commit()

        upsert_chunks([{
            "chunk_id": chunk_id,
            "document_id": document.id,
            "chunk_index": 0,
            "text": "Operating margin expanded to 18% in fiscal year 2024.",
            "embedding": [0.5] * vector_size,
            "file_name": "hybrid_test.txt",
            "source": "manual_upload"
        }])

        with patch("financial_intelligence_platform.services.retrieval.hybrid_search.dense_search") as mock_dense, \
             patch("financial_intelligence_platform.services.retrieval.hybrid_search.bm25_search") as mock_bm25:

            mock_dense.return_value = [{
                "chunk_id": chunk_id,
                "score": 0.9,
                "payload": {"document_id": document.id, "text": "Operating margin expanded"},
                "search_type": "dense"
            }]
            mock_bm25.return_value = [{
                "chunk_id": chunk_id,
                "score": 0.8,
                "payload": {"document_id": document.id, "text": "Operating margin expanded"},
                "search_type": "bm25"
            }]

            result = hybrid_search(
                db=db,
                query="operating margin",
                top_k=10,
                use_llm=False
            )

            assert result["original_query"] == "operating margin"
            assert len(result["results"]) >= 1
            assert result["results"][0]["chunk_id"] == chunk_id

    finally:
        db.query(Chunk).filter(Chunk.document_id == document.id).delete()
        db.query(Document).filter(Document.id == document.id).delete()
        db.commit()
        db.close()

        qdrant = get_qdrant_client()
        qdrant.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[chunk_id]
        )


def test_search_endpoint():
    response = client.post("/queries/search", json={
        "query": "revenue",
        "top_k": 5,
        "use_llm": False
    })

    assert response.status_code == 200
    data = response.json()
    assert data["original_query"] == "revenue"
    assert "results" in data
