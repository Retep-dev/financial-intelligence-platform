from typing import List, Optional
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    use_llm: Optional[bool] = True


class SearchResult(BaseModel):
    chunk_id: str
    score: float
    document_id: Optional[str] = None
    file_name: Optional[str] = None
    section: Optional[str] = None
    page_number: Optional[int] = None
    text: Optional[str] = None


class SearchResponse(BaseModel):
    original_query: str
    enhanced_query: dict
    dense_count: int
    bm25_count: int
    results: List[SearchResult]
