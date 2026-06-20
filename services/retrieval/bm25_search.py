from typing import List, Dict

from sqlalchemy import text, func
from sqlalchemy.orm import Session

from db.postgres.models.chunk import Chunk


def bm25_search(
    db: Session,
    query: str,
    top_k: int = 50
) -> List[Dict]:
    """Search chunks using PostgreSQL full-text search (BM25-like ranking)."""
    ts_query = func.plainto_tsquery("english", query)

    results = (
        db.query(
            Chunk,
            func.ts_rank_cd(
                func.to_tsvector("english", Chunk.chunk_text),
                ts_query
            ).label("rank")
        )
        .filter(
            func.to_tsvector("english", Chunk.chunk_text).op("@@")(ts_query)
        )
        .order_by(text("rank DESC"))
        .limit(top_k)
        .all()
    )

    return [
        {
            "chunk_id": chunk.embedding_id or chunk.id,
            "score": float(rank),
            "payload": {
                "document_id": chunk.document_id,
                "chunk_id": chunk.embedding_id or chunk.id,
                "chunk_index": chunk.chunk_index,
                "section": chunk.section,
                "page_number": chunk.page_number,
                "text": chunk.chunk_text,
            },
            "search_type": "bm25"
        }
        for chunk, rank in results
    ]
