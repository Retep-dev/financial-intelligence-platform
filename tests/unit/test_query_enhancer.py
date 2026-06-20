from unittest.mock import patch

from services.retrieval.query_enhancer import enhance_query, expand_abbreviations


def test_expand_abbreviations():
    query = "What was the EBITDA and EPS in Q1?"
    result = expand_abbreviations(query)
    assert "Earnings Before Interest" in result
    assert "Earnings Per Share" in result


def test_enhance_query_without_llm():
    query = "What was the revenue?"
    result = enhance_query(query, use_llm=False)

    assert result["original"] == query
    assert result["expanded"] == query
    assert result["rewritten"] == query
    assert result["retrieval_queries"] == [query]


def test_enhance_query_with_llm():
    mock_response = '{"rewritten": "What was the total revenue?", "retrieval_queries": ["What was the total revenue?", "revenue amount"]}'

    with patch("services.retrieval.query_enhancer.generate_text") as mock_generate:
        mock_generate.return_value = mock_response

        result = enhance_query("revenue?", use_llm=True)

        assert result["original"] == "revenue?"
        assert result["rewritten"] == "What was the total revenue?"
        assert len(result["retrieval_queries"]) == 2
