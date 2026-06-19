import os
import tempfile
import uuid
from unittest.mock import patch

from db.postgres.session import SessionLocal
from db.postgres.models.document import Document, DocumentStatus
from db.postgres.models.chunk import Chunk

from services.ingestion.service import create_document_record
from services.embeddings.client import get_embedding_dimensions
from workers.tasks.document_processing import process_document


def test_process_document_end_to_end():
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write("Revenue increased by 10% in Q1 2024. Net income was $1.5M.")
        path = f.name

    document = create_document_record(
        original_filename="report.txt",
        file_path=path
    )

    chunk_id_1 = str(uuid.uuid4())
    chunk_id_2 = str(uuid.uuid4())
    vector_size = get_embedding_dimensions()

    try:
        with patch("workers.tasks.document_processing.generate_chunk_embeddings") as mock_embed:
            mock_embed.return_value = [
                {
                    "chunk_id": chunk_id_1,
                    "document_id": document.id,
                    "chunk_index": 0,
                    "text": "Revenue increased by 10% in Q1 2024.",
                    "embedding": [0.0] * vector_size,
                    "file_name": "report.txt",
                    "source": "manual_upload"
                },
                {
                    "chunk_id": chunk_id_2,
                    "document_id": document.id,
                    "chunk_index": 1,
                    "text": "Net income was USD 1500000.",
                    "embedding": [0.0] * vector_size,
                    "file_name": "report.txt",
                    "source": "manual_upload"
                }
            ]

            result = process_document.run(document.id)

        assert result["status"] == "processed"
        assert result["chunks_processed"] == 2

        db = SessionLocal()
        try:
            updated_doc = db.query(Document).filter(Document.id == document.id).first()
            assert updated_doc.status == DocumentStatus.PROCESSED.value

            chunks = db.query(Chunk).filter(Chunk.document_id == document.id).all()
            assert len(chunks) == 2
            assert chunks[0].embedding_id == chunk_id_1
            assert chunks[1].embedding_id == chunk_id_2
        finally:
            db.close()

    finally:
        os.unlink(path)
