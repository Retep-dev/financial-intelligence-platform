from services.evaluation.metrics import (
    recall_at_k,
    precision_at_k,
    citation_accuracy,
    format_metrics
)


def test_recall_at_k():
    retrieved = ["a", "b", "c", "d"]
    expected = ["a", "c", "e"]

    assert recall_at_k(retrieved, expected, 1) == 1 / 3
    assert recall_at_k(retrieved, expected, 2) == 1 / 3
    assert recall_at_k(retrieved, expected, 3) == 2 / 3
    assert recall_at_k(retrieved, expected, 10) == 2 / 3


def test_precision_at_k():
    retrieved = ["a", "b", "c", "d"]
    expected = ["a", "c"]

    assert precision_at_k(retrieved, expected, 1) == 1.0
    assert precision_at_k(retrieved, expected, 2) == 0.5
    assert precision_at_k(retrieved, expected, 4) == 0.5


def test_citation_accuracy():
    retrieved = ["a", "b", "c"]
    citations = ["a", "b", "x"]

    assert citation_accuracy(citations, retrieved) == 2 / 3


def test_citation_accuracy_no_citations():
    assert citation_accuracy([], ["a", "b"]) == 1.0


def test_format_metrics():
    results = [
        {
            "retrieved_chunk_ids": ["a", "b", "c"],
            "expected_chunk_ids": ["a", "d"],
            "citation_chunk_ids": ["a"],
            "latency_ms": 100.0,
            "cost_usd": 0.01
        },
        {
            "retrieved_chunk_ids": ["x", "y"],
            "expected_chunk_ids": ["x"],
            "citation_chunk_ids": ["x"],
            "latency_ms": 200.0,
            "cost_usd": 0.02
        }
    ]

    metrics = format_metrics(results, k_values=[1, 2])

    # Recall@1: (0.5 + 1.0) / 2 = 0.75
    assert metrics["recall_at_k"][1] == 0.75
    # Recall@2: (0.5 + 1.0) / 2 = 0.75
    assert metrics["recall_at_k"][2] == 0.75
    # Precision@1: (1.0 + 1.0) / 2 = 1.0
    assert metrics["precision_at_k"][1] == 1.0
    assert metrics["citation_accuracy"] == 1.0
    assert metrics["avg_latency_ms"] == 150.0
    assert metrics["avg_cost_usd"] == 0.015
    assert metrics["total_examples"] == 2
