from typing import List, Dict


def build_citation_prompt(query: str, chunks: List[Dict]) -> tuple[str, str]:
    """Build system and user prompts for grounded answer generation with citations.

    Returns a tuple of (system_prompt, user_prompt).
    """
    system_prompt = (
        "You are a careful document Q&A assistant. Answer the user's question "
        "using ONLY the provided context. Do not use outside knowledge, assumptions, "
        "or invented details. Every factual claim must be cited with "
        "[citation: <chunk_id>]. If the context does not contain enough information, "
        "say exactly: 'I do not have enough information to answer this question.' "
        "Be concise, accurate, and grounded in the sources."
    )

    context_parts = []
    for i, chunk in enumerate(chunks, start=1):
        payload = chunk.get("payload", {})
        chunk_id = chunk.get("chunk_id") or payload.get("chunk_id", f"chunk_{i}")
        text = payload.get("text", "").strip()

        metadata = []
        if payload.get("file_name"):
            metadata.append(f"Document: {payload['file_name']}")
        if payload.get("section"):
            metadata.append(f"Section: {payload['section']}")
        if payload.get("page_number"):
            metadata.append(f"Page: {payload['page_number']}")

        metadata_str = " | ".join(metadata)
        context_parts.append(
            f"[{i}] chunk_id: {chunk_id}{' | ' + metadata_str if metadata_str else ''}\n{text}"
        )

    context = "\n\n".join(context_parts)

    user_prompt = (
        f"Question: {query}\n\n"
        f"Context:\n{context}\n\n"
        "Answer the question using only the context above. "
        "Cite every factual claim with [citation: <chunk_id>]."
    )

    return system_prompt, user_prompt
