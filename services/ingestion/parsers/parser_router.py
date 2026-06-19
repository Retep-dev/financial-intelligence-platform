import re
from pathlib import Path
from services.ingestion.parsers.pdf_parser import extract_pdf_text
from services.ingestion.preprocessing.text_cleaner import clean_text
from services.ingestion.preprocessing.structure_fix import fix_structure
from services.ingestion.preprocessing.layout_normalizer import normalize_layout


def extract_text(file_path: str) -> str:

    extension = Path(file_path).suffix.lower()
    if extension == ".pdf":
        return extract_pdf_text(file_path)

        clean = re.sub(r"\s+", " ", raw)

        return clean

    elif extension in [".docx", ".doc"]:
        return "DOCX parsing not implemented yet"

    elif extension in [".xlsx", ".csv"]:
        return "Spreadsheet parsing not implemented yet"

    elif extension == ".txt":
        return clean_text(open(file_path, "r", encoding="utf-8").read())

    elif extension == ".html":
        return "HTML parsing not implemented yet"

    else:
        raise ValueError(f"Unsupported file type: {extension}")
