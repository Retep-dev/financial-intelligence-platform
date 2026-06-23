import re


def clean_text(text: str) -> str:

    # Fix broken hyphenation across lines
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Remove non-ASCII noise
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Fix excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove bullet artifacts
    text = text.replace("●", " ").replace("•", " ")

    # Fix broken words like "appointm Records"
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()
