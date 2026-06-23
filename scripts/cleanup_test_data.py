"""Remove test fixture documents and chunks left behind by integration tests."""
from sqlalchemy.orm import Session
from qdrant_client.models import Filter, FieldCondition, MatchValue

from financial_intelligence_platform.db.postgres.session import SessionLocal
from financial_intelligence_platform.db.postgres.models.document import Document
from financial_intelligence_platform.db.postgres.models.chunk import Chunk
from financial_intelligence_platform.db.qdrant.client import get_qdrant_client
from financial_intelligence_platform.db.qdrant.collections import COLLECTION_NAME
from financial_intelligence_platform.db.qdrant.queries import delete_document_chunks


TEST_FILE_NAMES = {
    "report.txt",
    "bm25_test.txt",
    "hybrid_test.txt",
    "earnings.txt",
    "citation_test.txt",
    "Q4_2024.pdf",
    "earnings.pdf",
}


def cleanup_postgres(db: Session) -> int:
    documents = db.query(Document).filter(Document.file_name.in_(TEST_FILE_NAMES)).all()
    doc_ids = [doc.id for doc in documents]

    for doc_id in doc_ids:
        delete_document_chunks(doc_id)

    if doc_ids:
        db.query(Chunk).filter(Chunk.document_id.in_(doc_ids)).delete(synchronize_session=False)
        for doc in documents:
            db.delete(doc)
        db.commit()

    return len(documents)


def cleanup_qdrant() -> None:
    """Delete any Qdrant points whose payload file_name matches test fixtures."""
    client = get_qdrant_client()
    for file_name in TEST_FILE_NAMES:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="file_name",
                        match=MatchValue(value=file_name)
                    )
                ]
            )
        )


if __name__ == "__main__":
    db = SessionLocal()
    try:
        postgres_count = cleanup_postgres(db)
        cleanup_qdrant()
        print(f"Deleted {postgres_count} test documents from PostgreSQL")
        print("Cleaned Qdrant payloads for test file names")
    finally:
        db.close()
