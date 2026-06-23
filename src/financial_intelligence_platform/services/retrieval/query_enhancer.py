import json
import re

from financial_intelligence_platform.services.generation.client import generate_text


DOMAIN_ABBREVIATIONS = {
    " YoY ": " year over year ",
    " QoQ ": " quarter over quarter ",
}


def expand_abbreviations(query: str) -> str:
    """Expand common domain-agnostic abbreviations in the query."""
    for abbreviation, expansion in DOMAIN_ABBREVIATIONS.items():
        pattern = re.compile(re.escape(abbreviation), re.IGNORECASE)
        query = pattern.sub(f" {expansion} ", query)
    return re.sub(r"\s+", " ", query).strip()


def enhance_query(query: str, use_llm: bool = True) -> dict:
    """Enhance a user query for better retrieval.

    Returns a dict with:
      - original
      - expanded (abbreviations expanded)
      - rewritten (LLM rewritten for retrieval)
      - retrieval_queries (list of query variants)
    """
    expanded = expand_abbreviations(query)

    if not use_llm:
        return {
            "original": query,
            "expanded": expanded,
            "rewritten": expanded,
            "retrieval_queries": [expanded]
        }

    system_prompt = (
        "You are a search query optimizer for a document retrieval system. "
        "Rewrite the user's question into a clear, retrieval-friendly query. "
        "Do not add assumptions about currency, amounts, or domain-specific details "
        "that are not in the original question. "
        "Return ONLY a JSON object with keys: rewritten, retrieval_queries. "
        "retrieval_queries should be a list of 1-3 query variants."
    )

    try:
        response = generate_text(
            system_prompt=system_prompt,
            user_prompt=f"Query: {expanded}",
            temperature=0.0
        )

        # Extract JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            rewritten = parsed.get("rewritten", expanded)
            retrieval_queries = parsed.get("retrieval_queries", [expanded])
        else:
            rewritten = response
            retrieval_queries = [expanded]

    except Exception:
        rewritten = expanded
        retrieval_queries = [expanded]

    return {
        "original": query,
        "expanded": expanded,
        "rewritten": rewritten,
        "retrieval_queries": retrieval_queries[:3]
    }
