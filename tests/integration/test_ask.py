from unittest.mock import patch

from fastapi.testclient import TestClient

from financial_intelligence_platform.main import app

client = TestClient(app)


def test_ask_endpoint():
    with patch("financial_intelligence_platform.services.retrieval.ask.generate_answer") as mock_answer, \
         patch("financial_intelligence_platform.services.retrieval.ask.hybrid_search") as mock_search, \
         patch("financial_intelligence_platform.services.retrieval.ask.build_citations") as mock_citations:

        chunk_id = "chunk-test-123"

        mock_search.return_value = {
            "original_query": "What was the revenue?",
            "enhanced_query": {},
            "dense_count": 1,
            "bm25_count": 0,
            "reranked_count": 1,
            "results": [{
                "chunk_id": chunk_id,
                "score": 0.95,
                "payload": {
                    "document_id": "doc-123",
                    "file_name": "earnings.pdf",
                    "section": "Revenue",
                    "page_number": 2,
                    "text": "Revenue increased by 12% to USD 4.2 billion."
                }
            }]
        }

        mock_answer.return_value = (
            "Revenue increased by 12% to USD 4.2 billion [citation: chunk-test-123]."
        )

        mock_citations.return_value = [{
            "chunk_id": chunk_id,
            "document_id": "doc-123",
            "document_name": "earnings.pdf",
            "section": "Revenue",
            "page_number": 2,
            "text": "Revenue increased by 12% to USD 4.2 billion."
        }]

        response = client.post("/queries/ask", json={
            "query": "What was the revenue?",
            "top_k": 5,
            "top_n": 3,
            "use_llm": False
        })

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "What was the revenue?"
        assert "USD 4.2 billion" in data["answer"]
        assert len(data["citations"]) == 1
        assert data["citations"][0]["chunk_id"] == chunk_id
        assert data["citations"][0]["document_name"] == "earnings.pdf"
