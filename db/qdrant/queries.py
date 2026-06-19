from typing import List, Dict

from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue

from db.qdrant.client import get_qdrant_client
from db.qdrant.collections import COLLECTION_NAME


def upsert_chunks(chunks: List[Dict]) -> None:
    """Upsert chunks with embeddings into Qdrant."""
    if not chunks:
        return

    client = get_qdrant_client()

    points = []
    for chunk in chunks:
        if "embedding" not in chunk or "chunk_id" not in chunk:
            continue

        points.append(
            PointStruct(
                id=chunk["chunk_id"],
                vector=chunk["embedding"],
                payload={
                    "document_id": chunk.get("document_id"),
                    "chunk_id": chunk["chunk_id"],
                    "chunk_index": chunk.get("chunk_index"),
                    "section": chunk.get("section"),
                    "page_number": chunk.get("page_number"),
                    "file_name": chunk.get("file_name"),
                    "source": chunk.get("source"),
                    "text": chunk.get("text"),
                }
            )
        )

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True
        )


def delete_document_chunks(document_id: str) -> None:
    """Delete all chunks for a given document."""
    client = get_qdrant_client()

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )
