"""Inspect chunks for a given document."""
import sys

from financial_intelligence_platform.db.postgres.session import SessionLocal
from financial_intelligence_platform.db.postgres.models.document import Document
from financial_intelligence_platform.db.postgres.models.chunk import Chunk


def inspect(filename: str):
    db = SessionLocal()
    try:
        documents = db.query(Document).filter(Document.file_name == filename).all()
        if not documents:
            print(f"No documents found with file_name={filename}")
            return

        for doc in documents:
            print(f"\nDocument: {doc.file_name} (id={doc.id}, status={doc.status}, pages={doc.page_count})")
            chunks = (
                db.query(Chunk)
                .filter(Chunk.document_id == doc.id)
                .order_by(Chunk.chunk_index)
                .all()
            )
            print(f"Chunks: {len(chunks)}")
            for i, chunk in enumerate(chunks[:10]):
                print(f"\n--- Chunk {i} (index={chunk.chunk_index}) ---")
                print(chunk.chunk_text[:500])
            if len(chunks) > 10:
                print(f"\n... and {len(chunks) - 10} more chunks")
    finally:
        db.close()


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "FS.pdf"
    inspect(filename)
