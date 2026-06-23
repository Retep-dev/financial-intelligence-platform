from pathlib import Path

from financial_intelligence_platform.workers.celery_app import celery_app

from financial_intelligence_platform.db.postgres.models.document import Document, DocumentStatus
from financial_intelligence_platform.db.postgres.models.chunk import ChunkStatus
from financial_intelligence_platform.db.postgres.session import SessionLocal

from financial_intelligence_platform.services.ingestion.parsers.parser_router import extract_text
from financial_intelligence_platform.services.ingestion.service import update_document_status
from financial_intelligence_platform.services.chunking.chunker import split_into_chunks
from financial_intelligence_platform.services.chunking.chunk_repository import save_chunks
from financial_intelligence_platform.services.embeddings.generator import generate_chunk_embeddings

from financial_intelligence_platform.db.qdrant.collections import ensure_collection_exists
from financial_intelligence_platform.db.qdrant.queries import upsert_chunks, delete_document_chunks


@celery_app.task(bind=True, max_retries=3)
def process_document(self, document_id: str):
    db = SessionLocal()

    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise ValueError(f"Document {document_id} not found")

        update_document_status(
            document_id=document.id,
            status=DocumentStatus.PROCESSING
        )

        # Delete old chunks from Qdrant if reprocessing
        delete_document_chunks(document.id)

        # Extract and preprocess text
        text = extract_text(document.file_path)

        # Determine page count for PDFs
        page_count = None
        if document.document_type.lower() == ".pdf":
            from fitz import open as fitz_open
            with fitz_open(document.file_path) as doc:
                page_count = len(doc)

        # Chunk text
        chunks = split_into_chunks(
            text=text,
            document_id=document.id
        )

        # Enrich chunks with metadata for Qdrant payload
        for index, chunk in enumerate(chunks):
            chunk["chunk_index"] = index
            chunk["file_name"] = document.file_name
            chunk["source"] = document.source

        # Generate embeddings
        chunks = generate_chunk_embeddings(chunks)

        # Prepare chunks for database storage
        db_chunks = []
        for chunk in chunks:
            db_chunks.append({
                "text": chunk["text"],
                "chunk_index": chunk["chunk_index"],
                "section": chunk.get("section"),
                "page_number": chunk.get("page_number"),
                "token_count": chunk.get("token_count"),
                "embedding_id": chunk["chunk_id"],
                "status": ChunkStatus.EMBEDDED.value
            })

        # Save chunks to PostgreSQL
        save_chunks(
            db=db,
            document_id=document.id,
            chunks=db_chunks
        )

        # Ensure Qdrant collection exists and upsert vectors
        ensure_collection_exists()
        upsert_chunks(chunks)

        # Mark document as processed
        update_document_status(
            document_id=document.id,
            status=DocumentStatus.PROCESSED,
            page_count=page_count
        )

        return {
            "document_id": document.id,
            "chunks_processed": len(chunks),
            "status": "processed"
        }

    except Exception as exc:
        update_document_status(
            document_id=document_id,
            status=DocumentStatus.FAILED
        )
        raise self.retry(exc=exc, countdown=60)

    finally:
        db.close()
