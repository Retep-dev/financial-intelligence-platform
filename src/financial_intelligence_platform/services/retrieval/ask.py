from typing import List, Dict
from sqlalchemy.orm import Session

from financial_intelligence_platform.services.retrieval.hybrid_search import hybrid_search
from financial_intelligence_platform.services.generation.generator import generate_answer
from financial_intelligence_platform.services.generation.response_parser import extract_citation_markers, normalize_citation_text
from financial_intelligence_platform.services.citations.builder import build_citations
from financial_intelligence_platform.services.citations.formatter import format_citations


def ask_question(
    db: Session,
    query: str,
    top_k: int = 50,
    top_n: int = 10,
    use_llm: bool = True
) -> Dict:
    """End-to-end RAG: retrieve → generate → cite."""
    retrieval_result = hybrid_search(
        db=db,
        query=query,
        top_k=top_k,
        top_n=top_n,
        use_llm=use_llm
    )

    chunks = retrieval_result["results"]

    if not chunks:
        return {
            "query": query,
            "answer": "I do not have enough information to answer this question.",
            "citations": [],
            "citation_texts": [],
            "retrieval_metadata": {
                "dense_count": retrieval_result["dense_count"],
                "bm25_count": retrieval_result["bm25_count"],
                "reranked_count": retrieval_result["reranked_count"]
            }
        }

    answer = generate_answer(query, chunks)
    chunk_ids = extract_citation_markers(answer)
    citations = build_citations(db, chunk_ids)
    citation_texts = format_citations(citations)
    display_answer = normalize_citation_text(answer)

    return {
        "query": query,
        "answer": display_answer,
        "citations": citations,
        "citation_texts": citation_texts,
        "retrieval_metadata": {
            "dense_count": retrieval_result["dense_count"],
            "bm25_count": retrieval_result["bm25_count"],
            "reranked_count": retrieval_result["reranked_count"]
        }
    }
