from typing import List, Dict

from financial_intelligence_platform.db.qdrant.client import get_qdrant_client
from financial_intelligence_platform.db.qdrant.collections import COLLECTION_NAME
from financial_intelligence_platform.services.embeddings.generator import generate_embeddings


def dense_search(
    query: str,
    top_k: int = 50,
    filters: Dict = None
) -> List[Dict]:
    """Search Qdrant using dense vector similarity."""
    client = get_qdrant_client()

    # Generate query embedding
    embeddings = generate_embeddings([query], input_type="query")
    if not embeddings:
        return []

    query_vector = embeddings[0]

    search_kwargs = {
        "collection_name": COLLECTION_NAME,
        "query": query_vector,
        "limit": top_k,
        "with_payload": True,
    }

    if filters:
        search_kwargs["query_filter"] = filters

    results = client.query_points(**search_kwargs)

    return [
        {
            "chunk_id": point.id,
            "score": point.score,
            "payload": point.payload,
            "search_type": "dense"
        }
        for point in results.points
    ]
