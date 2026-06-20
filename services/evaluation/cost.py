from typing import Dict, List

from core.config.settings import settings


# Approximate pricing in USD per 1M tokens
EMBEDDING_PRICES = {
    "nvidia": 0.01,
    "openai": 0.13,
}

GENERATION_PRICES = {
    "nvidia": {
        "input": 0.50,
        "output": 1.50,
    },
    "openai": {
        "input": 0.15,
        "output": 0.60,
    }
}

RERANK_PRICE_PER_1M = 2.00


def estimate_token_count(text: str) -> int:
    """Rough token estimate: ~0.75 tokens per word for English."""
    return int(len(text.split()) * 0.75)


def estimate_embedding_cost(texts: List[str]) -> float:
    """Estimate embedding cost for a list of texts."""
    total_tokens = sum(estimate_token_count(t) for t in texts)
    price_per_1m = EMBEDDING_PRICES.get(settings.EMBEDDING_PROVIDER.lower(), 0.01)
    return (total_tokens / 1_000_000) * price_per_1m


def estimate_generation_cost(input_text: str, output_text: str) -> float:
    """Estimate generation cost for input and output tokens."""
    input_tokens = estimate_token_count(input_text)
    output_tokens = estimate_token_count(output_text)

    provider = settings.GENERATION_PROVIDER.lower()
    prices = GENERATION_PRICES.get(provider, GENERATION_PRICES["openai"])

    input_cost = (input_tokens / 1_000_000) * prices["input"]
    output_cost = (output_tokens / 1_000_000) * prices["output"]

    return input_cost + output_cost


def estimate_rerank_cost(query: str, documents: List[str]) -> float:
    """Estimate Cohere rerank cost."""
    total_tokens = estimate_token_count(query) + sum(
        estimate_token_count(doc) for doc in documents
    )
    return (total_tokens / 1_000_000) * RERANK_PRICE_PER_1M
