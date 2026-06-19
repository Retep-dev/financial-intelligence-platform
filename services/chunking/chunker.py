import re
import uuid
from typing import List, Dict


def estimate_token_count(text: str) -> int:
    """Rough token estimate: ~0.75 tokens per word for English text."""
    return int(len(text.split()) * 0.75)


def split_into_chunks(
    text: str,
    document_id: str = None,
    chunk_size: int = 768,
    overlap: int = 96
) -> List[Dict]:

    # STEP 1: Detect likely headings (basic structure hinting)
    sections = [text]

    chunks = []

    for section in sections:
        sentences = re.split(r'(?<=[.!?]) +', section)

        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > chunk_size and current_chunk:

                chunk_text = " ".join(current_chunk).strip()
                chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "text": chunk_text,
                    "section": None,
                    "page_number": None,
                    "length": current_length,
                    "token_count": estimate_token_count(chunk_text)
                })

                # overlap handling
                current_chunk = current_chunk[-2:] if len(
                    current_chunk) > 2 else current_chunk
                current_length = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length

        if current_chunk:
            chunk_text = " ".join(current_chunk).strip()
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "document_id": document_id,
                "text": chunk_text,
                "section": None,
                "page_number": None,
                "length": current_length,
                "token_count": estimate_token_count(chunk_text)
            })

    return chunks
