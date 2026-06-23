import uuid

from financial_intelligence_platform.db.postgres.session import SessionLocal
from financial_intelligence_platform.db.postgres.models.document import Document
from financial_intelligence_platform.db.postgres.models.chunk import Chunk

from financial_intelligence_platform.services.ingestion.service import create_document_record
from financial_intelligence_platform.services.citations.builder import build_citations


def test_build_citations():
    document = create_document_record(
        original_filename="citation_test.txt",
        file_path="/tmp/citation_test.txt"
    )

    chunk_id = str(uuid.uuid4())

    db = SessionLocal()
    try:
        chunk = Chunk(
            document_id=document.id,
            chunk_index=0,
            chunk_text="Revenue was USD 1 billion.",
            section="Financial Highlights",
            page_number=3,
            embedding_id=chunk_id,
            status="embedded"
        )
        db.add(chunk)
        db.commit()

        citations = build_citations(db, [chunk_id])

        assert len(citations) == 1
        assert citations[0]["chunk_id"] == chunk_id
        assert citations[0]["document_name"] == "citation_test.txt"
        assert citations[0]["section"] == "Financial Highlights"
        assert citations[0]["page_number"] == 3

    finally:
        db.query(Chunk).filter(Chunk.document_id == document.id).delete()
        db.commit()
        db.close()
