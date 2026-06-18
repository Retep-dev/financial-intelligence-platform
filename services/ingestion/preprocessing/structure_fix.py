import re


def fix_structure(text: str) -> str:

    # Fix broken sentence joins
    text = re.sub(r"([a-z])([A-Z])", r"\1. \2", text)

    # Fix weird line joins
    text = text.replace("\n", " ")

    return text
