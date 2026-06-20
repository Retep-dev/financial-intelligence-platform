from typing import List, Dict
from sqlalchemy.orm import Session

from db.postgres.models.chunk import Chunk
from db.postgres.models.document import Document


def build_citations(db: Session, chunk_ids: List[str]) -> List[Dict]:
    """Resolve chunk IDs to full citation metadata."""
    if not chunk_ids:
        return []

    chunks = (
        db.query(Chunk, Document)
        .join(Document, Chunk.document_id == Document.id)
        .filter(Chunk.embedding_id.in_(chunk_ids))
        .all()
    )

    citations = []
    seen = set()

    for chunk, document in chunks:
        if chunk.embedding_id in seen:
            continue
        seen.add(chunk.embedding_id)

        citations.append({
            "chunk_id": chunk.embedding_id,
            "document_id": document.id,
            "document_name": document.file_name,
            "page_number": chunk.page_number,
            "section": chunk.section,
            "text": chunk.chunk_text
        })

    # Preserve order of appearance in chunk_ids
    order = {cid: idx for idx, cid in enumerate(chunk_ids)}
    citations.sort(key=lambda c: order.get(c["chunk_id"], 9999))

    return citations
