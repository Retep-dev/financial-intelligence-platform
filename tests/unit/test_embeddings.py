from unittest.mock import patch, MagicMock

from financial_intelligence_platform.services.embeddings.generator import generate_embeddings, generate_chunk_embeddings


def test_generate_embeddings():
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1, 0.2, 0.3]),
        MagicMock(embedding=[0.4, 0.5, 0.6]),
    ]

    with patch("financial_intelligence_platform.services.embeddings.generator.get_embedding_client") as mock_client:
        mock_client.return_value.embeddings.create.return_value = mock_response

        embeddings = generate_embeddings(["hello", "world"])

        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]


def test_generate_chunk_embeddings():
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1, 0.2, 0.3]),
    ]

    with patch("financial_intelligence_platform.services.embeddings.generator.get_embedding_client") as mock_client:
        mock_client.return_value.embeddings.create.return_value = mock_response

        chunks = [{"text": "Revenue increased."}]
        result = generate_chunk_embeddings(chunks)

        assert "embedding" in result[0]
        assert result[0]["embedding"] == [0.1, 0.2, 0.3]
