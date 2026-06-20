from typing import List, Optional
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 50
    top_n: Optional[int] = 10
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
    reranked_count: int
    results: List[SearchResult]


class AskRequest(BaseModel):
    query: str
    top_k: Optional[int] = 50
    top_n: Optional[int] = 10
    use_llm: Optional[bool] = True


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    text: Optional[str] = None


class AskResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    citation_texts: List[str]
    retrieval_metadata: dict
