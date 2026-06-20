from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies.db import get_db
from api.schemas.query import SearchRequest, SearchResponse, SearchResult
from services.retrieval.hybrid_search import hybrid_search

router = APIRouter(
    prefix="/queries",
    tags=["Queries"]
)


@router.post("/search", response_model=SearchResponse)
def search_chunks(request: SearchRequest, db: Session = Depends(get_db)):
    result = hybrid_search(
        db=db,
        query=request.query,
        top_k=request.top_k,
        top_n=request.top_n,
        use_llm=request.use_llm
    )

    results = []
    for item in result["results"]:
        payload = item.get("payload", {})
        results.append(SearchResult(
            chunk_id=item["chunk_id"],
            score=item["score"],
            document_id=payload.get("document_id"),
            file_name=payload.get("file_name"),
            section=payload.get("section"),
            page_number=payload.get("page_number"),
            text=payload.get("text")
        ))

    return SearchResponse(
        original_query=result["original_query"],
        enhanced_query=result["enhanced_query"],
        dense_count=result["dense_count"],
        bm25_count=result["bm25_count"],
        reranked_count=result["reranked_count"],
        results=results
    )
