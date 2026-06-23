from unittest.mock import MagicMock, patch

from financial_intelligence_platform.services.reranking.reranker import rerank_chunks


def test_rerank_chunks_fallback_without_api_key():
    chunks = [
        {"chunk_id": "1", "score": 0.5, "payload": {"text": "Revenue was up."}},
        {"chunk_id": "2", "score": 0.8, "payload": {"text": "Profit increased."}},
    ]

    with patch("financial_intelligence_platform.services.reranking.reranker.settings.COHERE_API_KEY", None):
        result = rerank_chunks("revenue", chunks, top_n=2)

    assert len(result) == 2
    assert result[0]["chunk_id"] == "2"


def test_rerank_chunks_with_cohere():
    chunks = [
        {"chunk_id": "1", "score": 0.5, "payload": {"text": "Revenue was up."}},
        {"chunk_id": "2", "score": 0.8, "payload": {"text": "Profit increased."}},
    ]

    mock_response = MagicMock()
    mock_response.results = [
        MagicMock(index=1, relevance_score=0.95),
        MagicMock(index=0, relevance_score=0.85),
    ]

    with patch("financial_intelligence_platform.services.reranking.reranker.get_cohere_client") as mock_client:
        mock_client.return_value.rerank.return_value = mock_response

        result = rerank_chunks("revenue", chunks, top_n=2)

        assert len(result) == 2
        assert result[0]["chunk_id"] == "2"
        assert result[0]["score"] == 0.95
