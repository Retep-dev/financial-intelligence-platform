import json
import re

from services.generation.client import generate_text


FINANCIAL_ABBREVIATIONS = {
    "EBITDA": "Earnings Before Interest, Taxes, Depreciation, and Amortization",
    "EBIT": "Earnings Before Interest and Taxes",
    "EPS": "Earnings Per Share",
    "P/E": "Price-to-Earnings ratio",
    "GAAP": "Generally Accepted Accounting Principles",
    "IFRS": "International Financial Reporting Standards",
    "ROI": "Return on Investment",
    "ROE": "Return on Equity",
    "ROA": "Return on Assets",
    "NAV": "Net Asset Value",
    "AUM": "Assets Under Management",
    "IPO": "Initial Public Offering",
    "M&A": "Mergers and Acquisitions",
    " YoY ": " year over year ",
    " QoQ ": " quarter over quarter ",
}


def expand_abbreviations(query: str) -> str:
    """Expand common financial abbreviations in the query."""
    for abbreviation, expansion in FINANCIAL_ABBREVIATIONS.items():
        # Case-insensitive replacement with word boundaries where appropriate
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
        "You are a search query optimizer for a financial document retrieval system. "
        "Rewrite the user's question into a clear, retrieval-friendly query. "
        "Expand abbreviations and add financial domain context. "
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
