from unittest.mock import patch

from services.generation.generator import generate_answer
from services.generation.response_parser import (
    extract_citation_markers,
    normalize_citation_text
)


def test_generate_answer():
    chunks = [
        {
            "chunk_id": "chunk-abc",
            "payload": {
                "text": "Revenue increased by 12% to USD 4.2 billion.",
                "file_name": "Q4_2024.pdf"
            }
        }
    ]

    with patch("services.generation.generator.generate_text") as mock_generate:
        mock_generate.return_value = "Revenue increased by 12% [citation: chunk-abc]."

        answer = generate_answer("What was revenue?", chunks)
        assert "Revenue increased" in answer
        assert "[citation: chunk-abc]" in answer


def test_extract_citation_markers():
    text = "Revenue grew [citation: chunk-1] and profit rose [citation: chunk-2]."
    markers = extract_citation_markers(text)
    assert markers == ["chunk-1", "chunk-2"]


def test_normalize_citation_text():
    text = "Revenue grew [citation: chunk-1] and profit rose [citation: chunk-2]."
    normalized = normalize_citation_text(text)
    assert "[1]" in normalized
    assert "[2]" in normalized
    assert "[citation:" not in normalized
