from typing import List, Dict


def format_citations(citations: List[Dict]) -> List[str]:
    """Format citations as human-readable source lines."""
    lines = []
    for citation in citations:
        parts = [
            f"Document: {citation['document_name']}",
        ]
        if citation.get("section"):
            parts.append(f"Section: {citation['section']}")
        if citation.get("page_number"):
            parts.append(f"Page: {citation['page_number']}")
        parts.append(f"Chunk ID: {citation['chunk_id']}")

        lines.append(" | ".join(parts))

    return lines
