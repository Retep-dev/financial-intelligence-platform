from datetime import datetime

from db.postgres.models.chunk import Chunk, ChunkStatus


def save_chunks(db, document_id, chunks):

    db.query(Chunk).filter(
        Chunk.document_id == document_id
    ).delete(synchronize_session=False)

    for index, chunk in enumerate(chunks):

        db_chunk = Chunk(
            document_id=document_id,
            chunk_index=index,
            chunk_text=chunk["text"],
            section=chunk.get("section"),
            page_number=chunk.get("page_number"),
            token_count=chunk.get("token_count"),
            embedding_id=chunk.get("embedding_id"),
            status=chunk.get("status", ChunkStatus.PENDING.value),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(db_chunk)

    db.commit()
