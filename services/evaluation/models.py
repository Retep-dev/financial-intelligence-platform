from typing import List, Optional, Dict
from pydantic import BaseModel


class EvaluationExample(BaseModel):
    query: str
    expected_chunk_ids: List[str]
    acceptable_answers: Optional[List[str]] = None


class EvaluationResult(BaseModel):
    query: str
    retrieved_chunk_ids: List[str]
    answer: Optional[str] = None
    citation_chunk_ids: List[str] = []
    latency_ms: float = 0.0
    cost_usd: float = 0.0


class EvaluationMetrics(BaseModel):
    recall_at_k: Dict[int, float]
    precision_at_k: Dict[int, float]
    citation_accuracy: float
    hallucination_rate: float
    avg_latency_ms: float
    avg_cost_usd: float
    total_examples: int
