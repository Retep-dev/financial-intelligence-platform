import re
from typing import List, Dict

from financial_intelligence_platform.services.generation.client import generate_text
from financial_intelligence_platform.services.generation.prompt_builder import build_citation_prompt


def generate_answer(query: str, chunks: List[Dict], temperature: float = 0.0) -> str:
    """Generate a grounded answer with citation markers from retrieved chunks."""
    if not chunks:
        return "I do not have enough information to answer this question."

    system_prompt, user_prompt = build_citation_prompt(query, chunks)

    return generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature
    )
