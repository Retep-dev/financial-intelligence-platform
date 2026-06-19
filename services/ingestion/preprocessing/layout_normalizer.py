import re


def normalize_layout(text: str) -> str:

    # join broken lines
    text = text.replace("\n", " ")

    # fix multiple spaces
    text = re.sub(r"\s+", " ", text)

    # fix broken words caused by PDF extraction
    text = re.sub(r"(\w)\s+(\w)", r"\1 \2", text)

    # fix weird spacing around punctuation
    text = re.sub(r"\s+([.,;:])", r"\1", text)

    return text.strip()
