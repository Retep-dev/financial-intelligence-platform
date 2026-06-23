from typing import List, Dict


def recall_at_k(retrieved: List[str], expected: List[str], k: int) -> float:
    """Fraction of expected chunks found in top-K retrieved chunks."""
    if not expected:
        return 0.0

    retrieved_k = set(retrieved[:k])
    expected_set = set(expected)
    relevant_found = len(retrieved_k & expected_set)

    return relevant_found / len(expected_set)


def precision_at_k(retrieved: List[str], expected: List[str], k: int) -> float:
    """Fraction of top-K retrieved chunks that are relevant."""
    if k == 0 or not retrieved:
        return 0.0

    retrieved_k = retrieved[:k]
    expected_set = set(expected)
    relevant_found = sum(1 for cid in retrieved_k if cid in expected_set)

    return relevant_found / len(retrieved_k)


def citation_accuracy(citation_chunk_ids: List[str], retrieved: List[str]) -> float:
    """Fraction of citations that point to retrieved chunks."""
    if not citation_chunk_ids:
        return 1.0  # No citations is technically accurate

    retrieved_set = set(retrieved)
    valid_citations = sum(1 for cid in citation_chunk_ids if cid in retrieved_set)

    return valid_citations / len(citation_chunk_ids)


def average_metric(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def format_metrics(
    results: List[Dict],
    k_values: List[int] = None
) -> Dict:
    """Compute evaluation metrics from a list of result dicts."""
    if k_values is None:
        k_values = [1, 5, 10]

    recall_at_k_values = {k: [] for k in k_values}
    precision_at_k_values = {k: [] for k in k_values}
    citation_accuracies = []
    latencies = []
    costs = []

    for result in results:
        retrieved = result.get("retrieved_chunk_ids", [])
        expected = result.get("expected_chunk_ids", [])
        citations = result.get("citation_chunk_ids", [])

        for k in k_values:
            recall_at_k_values[k].append(recall_at_k(retrieved, expected, k))
            precision_at_k_values[k].append(precision_at_k(retrieved, expected, k))

        citation_accuracies.append(citation_accuracy(citations, retrieved))
        latencies.append(result.get("latency_ms", 0.0))
        costs.append(result.get("cost_usd", 0.0))

    return {
        "recall_at_k": {k: average_metric(recall_at_k_values[k]) for k in k_values},
        "precision_at_k": {k: average_metric(precision_at_k_values[k]) for k in k_values},
        "citation_accuracy": average_metric(citation_accuracies),
        "avg_latency_ms": average_metric(latencies),
        "avg_cost_usd": average_metric(costs),
        "total_examples": len(results)
    }
