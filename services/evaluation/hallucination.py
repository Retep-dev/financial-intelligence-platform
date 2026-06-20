from typing import Optional

from services.generation.client import generate_text


def detect_hallucination(answer: str, context: str) -> bool:
    """Use an LLM judge to detect unsupported claims in the answer.

    Returns True if hallucination is detected, False otherwise.
    """
    if not answer or not context:
        return False

    system_prompt = (
        "You are a strict fact-checker. Given a context and an answer, determine "
        "if the answer contains any claims that are NOT supported by the context. "
        "Respond with ONLY 'HALLUCINATION' if unsupported claims exist, or 'SUPPORTED' "
        "if all claims are grounded in the context."
    )

    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Answer:\n{answer}\n\n"
        "Is the answer fully supported by the context?"
    )

    try:
        response = generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0
        )
        return "HALLUCINATION" in response.upper()
    except Exception:
        return False
