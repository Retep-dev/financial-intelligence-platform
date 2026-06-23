from typing import List, Dict


def reciprocal_rank_fusion(
    rankings: List[List[Dict]],
    k: int = 60,
    top_n: int = 50
) -> List[Dict]:
    """Fuse multiple ranked lists using Reciprocal Rank Fusion.

    Each ranking item must contain 'chunk_id' and 'score'.
    """
    scores: Dict[str, float] = {}
    payloads: Dict[str, Dict] = {}

    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            chunk_id = item["chunk_id"]
            payload = item.get("payload", {})

            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
            payloads[chunk_id] = payload

    fused = [
        {
            "chunk_id": chunk_id,
            "score": score,
            "payload": payloads[chunk_id]
        }
        for chunk_id, score in scores.items()
    ]

    fused.sort(key=lambda x: x["score"], reverse=True)

    return fused[:top_n]
