from typing import List, Dict, Optional

import cohere

from financial_intelligence_platform.core.config.settings import settings


def get_cohere_client():
    if not settings.COHERE_API_KEY:
        raise ValueError("COHERE_API_KEY is not configured")
    return cohere.Client(api_key=settings.COHERE_API_KEY)


def _fallback_sort(chunks: List[Dict], top_n: int) -> List[Dict]:
    """Return top N chunks sorted by original score when reranker is unavailable."""
    sorted_chunks = sorted(
        chunks,
        key=lambda x: x.get("score", 0.0),
        reverse=True
    )
    return sorted_chunks[:top_n]


def rerank_chunks(
    query: str,
    chunks: List[Dict],
    top_n: int = 10,
    model: Optional[str] = None
) -> List[Dict]:
    """Rerank retrieved chunks using Cohere Rerank.

    Each chunk must have 'chunk_id' and 'payload.text'.
    Returns chunks sorted by reranker score.
    Falls back to score-based sorting if API key is missing or the call fails.
    """
    if not chunks:
        return chunks

    if not settings.COHERE_API_KEY:
        return _fallback_sort(chunks, top_n)

    try:
        client = get_cohere_client()
    except Exception:
        return _fallback_sort(chunks, top_n)

    model = model or settings.COHERE_RERANK_MODEL

    documents = []
    for chunk in chunks:
        payload = chunk.get("payload", {})
        text = payload.get("text", "")
        documents.append(text)

    try:
        response = client.rerank(
            model=model,
            query=query,
            documents=documents,
            top_n=min(top_n, len(documents)),
            return_documents=False
        )
    except Exception:
        return _fallback_sort(chunks, top_n)

    reranked = []
    for result in response.results:
        chunk = chunks[result.index]
        reranked.append({
            "chunk_id": chunk["chunk_id"],
            "score": result.relevance_score,
            "payload": chunk.get("payload", {}),
            "search_type": chunk.get("search_type", "reranked")
        })

    return reranked
