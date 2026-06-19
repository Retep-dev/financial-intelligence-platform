from db.qdrant.client import get_qdrant_client
from db.qdrant.collections import COLLECTION_NAME


def get_collection_stats() -> dict:
    """Return key statistics about the vector collection."""
    client = get_qdrant_client()
    info = client.get_collection(collection_name=COLLECTION_NAME)

    distance = info.config.params.vectors.distance
    distance_value = distance.value if hasattr(distance, "value") else str(distance)

    return {
        "collection": COLLECTION_NAME,
        "indexed_vectors_count": info.indexed_vectors_count,
        "points_count": info.points_count,
        "segments_count": info.segments_count,
        "vector_size": info.config.params.vectors.size,
        "distance": distance_value,
    }


def count_document_chunks(document_id: str) -> int:
    """Count how many chunks exist in Qdrant for a document."""
    client = get_qdrant_client()

    response = client.count(
        collection_name=COLLECTION_NAME,
        count_filter={
            "must": [
                {"key": "document_id", "match": {"value": document_id}}
            ]
        }
    )

    return response.count
