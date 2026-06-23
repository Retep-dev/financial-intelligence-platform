import re
import uuid
from typing import List, Dict


def estimate_token_count(text: str) -> int:
    """Rough token estimate: ~0.75 tokens per word for English text."""
    return int(len(text.split()) * 0.75)


def _split_long_sentence(sentence: str, max_tokens: int) -> List[str]:
    """Split a sentence that exceeds the token budget into smaller pieces."""
    words = sentence.split()
    pieces = []
    current_piece = []
    current_tokens = 0

    for word in words:
        word_tokens = max(1, int(len(word.split()) * 0.75))
        if current_tokens + word_tokens > max_tokens and current_piece:
            pieces.append(" ".join(current_piece))
            current_piece = []
            current_tokens = 0
        current_piece.append(word)
        current_tokens += word_tokens

    if current_piece:
        pieces.append(" ".join(current_piece))

    return pieces


def split_into_chunks(
    text: str,
    document_id: str = None,
    target_tokens: int = 150,
    overlap_tokens: int = 30
) -> List[Dict]:
    """Split text into chunks based on estimated token count.

    The default target of 384 tokens leaves a safety margin below common
    embedding model limits (e.g. 512 tokens).
    """
    max_sentence_tokens = target_tokens
    sentences = re.split(r'(?<=[.!?]) +', text)

    pieces = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if estimate_token_count(sentence) > max_sentence_tokens:
            pieces.extend(_split_long_sentence(sentence, max_sentence_tokens))
        else:
            pieces.append(sentence)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for piece in pieces:
        piece_tokens = estimate_token_count(piece)

        if current_tokens + piece_tokens > target_tokens and current_chunk:
            chunk_text = " ".join(current_chunk).strip()
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "document_id": document_id,
                "text": chunk_text,
                "section": None,
                "page_number": None,
                "length": len(chunk_text),
                "token_count": estimate_token_count(chunk_text)
            })

            # Keep pieces for overlap until overlap token budget is reached.
            overlap_chunk = []
            overlap_token_count = 0
            for p in reversed(current_chunk):
                p_tokens = estimate_token_count(p)
                if overlap_token_count + p_tokens > overlap_tokens and overlap_chunk:
                    break
                overlap_chunk.insert(0, p)
                overlap_token_count += p_tokens

            current_chunk = overlap_chunk
            current_tokens = overlap_token_count

        current_chunk.append(piece)
        current_tokens += piece_tokens

    if current_chunk:
        chunk_text = " ".join(current_chunk).strip()
        chunks.append({
            "chunk_id": str(uuid.uuid4()),
            "document_id": document_id,
            "text": chunk_text,
            "section": None,
            "page_number": None,
            "length": len(chunk_text),
            "token_count": estimate_token_count(chunk_text)
        })

    return chunks
