from typing import List, Dict

from sqlalchemy.orm import Session

from services.retrieval.query_enhancer import enhance_query
from services.retrieval.dense_search import dense_search
from services.retrieval.bm25_search import bm25_search
from services.retrieval.fusion import reciprocal_rank_fusion


def hybrid_search(
    db: Session,
    query: str,
    top_k: int = 50,
    use_llm: bool = True
) -> Dict:
    """Run hybrid retrieval: query enhancement → dense + BM25 → RRF fusion."""
    enhanced = enhance_query(query, use_llm=use_llm)

    retrieval_queries = enhanced["retrieval_queries"]

    # Dense search using the rewritten query
    dense_results = dense_search(
        query=enhanced["rewritten"],
        top_k=top_k
    )

    # BM25 search using all retrieval query variants
    bm25_results = []
    seen_ids = set()
    for q in retrieval_queries:
        for item in bm25_search(db=db, query=q, top_k=top_k):
            if item["chunk_id"] not in seen_ids:
                bm25_results.append(item)
                seen_ids.add(item["chunk_id"])

    fused = reciprocal_rank_fusion(
        rankings=[dense_results, bm25_results],
        k=60,
        top_n=top_k
    )

    return {
        "original_query": query,
        "enhanced_query": enhanced,
        "dense_count": len(dense_results),
        "bm25_count": len(bm25_results),
        "results": fused
    }
