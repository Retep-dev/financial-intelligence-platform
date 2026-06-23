import time
from typing import List, Dict

from sqlalchemy.orm import Session

from financial_intelligence_platform.services.evaluation.models import EvaluationExample
from financial_intelligence_platform.services.retrieval.ask import ask_question
from financial_intelligence_platform.services.retrieval.hybrid_search import hybrid_search
from financial_intelligence_platform.services.evaluation.metrics import (
    recall_at_k,
    precision_at_k,
    citation_accuracy,
    format_metrics
)
from financial_intelligence_platform.services.evaluation.hallucination import detect_hallucination
from financial_intelligence_platform.services.evaluation.cost import (
    estimate_embedding_cost,
    estimate_generation_cost,
    estimate_rerank_cost
)


def evaluate_example(
    db: Session,
    example: EvaluationExample,
    top_k: int = 10,
    top_n: int = 5,
    use_llm: bool = False
) -> Dict:
    """Evaluate a single example: retrieve, generate, measure, and score."""
    start_time = time.perf_counter()

    # Run end-to-end ask
    ask_result = ask_question(
        db=db,
        query=example.query,
        top_k=top_k,
        top_n=top_n,
        use_llm=use_llm
    )

    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000

    # Get retrieved chunks for metrics
    retrieval_result = hybrid_search(
        db=db,
        query=example.query,
        top_k=top_k,
        top_n=top_n,
        use_llm=use_llm
    )

    retrieved_chunk_ids = [r["chunk_id"] for r in retrieval_result["results"]]
    citation_chunk_ids = [c["chunk_id"] for c in ask_result["citations"]]

    # Build context text from retrieved chunks for hallucination check
    context_text = "\n\n".join(
        r.get("payload", {}).get("text", "") for r in retrieval_result["results"]
    )

    is_hallucination = detect_hallucination(
        answer=ask_result["answer"],
        context=context_text
    )

    # Estimate cost
    query_cost = estimate_embedding_cost([example.query])
    chunk_texts = [
        r.get("payload", {}).get("text", "") for r in retrieval_result["results"]
    ]
    embedding_cost = estimate_embedding_cost(chunk_texts)
    rerank_cost = estimate_rerank_cost(example.query, chunk_texts)
    generation_cost = estimate_generation_cost(
        input_text=context_text + "\n" + example.query,
        output_text=ask_result["answer"]
    )

    total_cost = query_cost + embedding_cost + rerank_cost + generation_cost

    return {
        "query": example.query,
        "expected_chunk_ids": example.expected_chunk_ids,
        "retrieved_chunk_ids": retrieved_chunk_ids,
        "answer": ask_result["answer"],
        "citation_chunk_ids": citation_chunk_ids,
        "latency_ms": latency_ms,
        "cost_usd": total_cost,
        "hallucination": is_hallucination
    }


def run_evaluation(
    db: Session,
    examples: List[EvaluationExample],
    top_k: int = 10,
    top_n: int = 5,
    use_llm: bool = False
) -> Dict:
    """Run evaluation over a dataset and return metrics."""
    results = []
    hallucination_count = 0

    for example in examples:
        result = evaluate_example(
            db=db,
            example=example,
            top_k=top_k,
            top_n=top_n,
            use_llm=use_llm
        )
        results.append(result)

        if result["hallucination"]:
            hallucination_count += 1

    metrics = format_metrics(results, k_values=[1, 5, 10])
    metrics["hallucination_rate"] = hallucination_count / len(results) if results else 0.0

    return {
        "metrics": metrics,
        "results": results
    }
