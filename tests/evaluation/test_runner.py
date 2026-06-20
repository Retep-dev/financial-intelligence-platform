from unittest.mock import patch, MagicMock

from services.evaluation.models import EvaluationExample
from services.evaluation.runner import evaluate_example, run_evaluation


def test_evaluate_example():
    example = EvaluationExample(
        query="What was the revenue?",
        expected_chunk_ids=["chunk-1"]
    )

    mock_ask_result = {
        "answer": "Revenue was USD 1 billion [citation: chunk-1].",
        "citations": [{"chunk_id": "chunk-1"}]
    }

    mock_retrieval_result = {
        "results": [
            {
                "chunk_id": "chunk-1",
                "payload": {"text": "Revenue was USD 1 billion."}
            }
        ]
    }

    with patch("services.evaluation.runner.ask_question", return_value=mock_ask_result), \
         patch("services.evaluation.runner.hybrid_search", return_value=mock_retrieval_result), \
         patch("services.evaluation.runner.detect_hallucination", return_value=False):

        result = evaluate_example(
            db=MagicMock(),
            example=example,
            top_k=5,
            top_n=3,
            use_llm=False
        )

        assert result["query"] == example.query
        assert result["retrieved_chunk_ids"] == ["chunk-1"]
        assert result["citation_chunk_ids"] == ["chunk-1"]
        assert result["latency_ms"] >= 0
        assert result["cost_usd"] >= 0
        assert result["hallucination"] is False


def test_run_evaluation():
    examples = [
        EvaluationExample(query="Q1", expected_chunk_ids=["chunk-1"]),
        EvaluationExample(query="Q2", expected_chunk_ids=["chunk-2"])
    ]

    mock_results = [
        {
            "query": "Q1",
            "expected_chunk_ids": ["chunk-1"],
            "retrieved_chunk_ids": ["chunk-1", "chunk-3"],
            "answer": "A1",
            "citation_chunk_ids": ["chunk-1"],
            "latency_ms": 100.0,
            "cost_usd": 0.01,
            "hallucination": False
        },
        {
            "query": "Q2",
            "expected_chunk_ids": ["chunk-2"],
            "retrieved_chunk_ids": ["chunk-2"],
            "answer": "A2",
            "citation_chunk_ids": ["chunk-2"],
            "latency_ms": 200.0,
            "cost_usd": 0.02,
            "hallucination": False
        }
    ]

    with patch("services.evaluation.runner.evaluate_example", side_effect=mock_results):
        report = run_evaluation(
            db=MagicMock(),
            examples=examples,
            top_k=5,
            top_n=3
        )

        assert report["metrics"]["total_examples"] == 2
        assert report["metrics"]["avg_latency_ms"] == 150.0
        assert report["metrics"]["hallucination_rate"] == 0.0
