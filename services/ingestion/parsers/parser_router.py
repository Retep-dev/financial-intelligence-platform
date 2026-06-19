from pathlib import Path

from services.ingestion.parsers.pdf_parser import extract_pdf_text
from services.ingestion.parsers.docx_parser import extract_docx_text
from services.ingestion.parsers.xlsx_parser import extract_xlsx_text
from services.ingestion.parsers.csv_parser import extract_csv_text
from services.ingestion.parsers.txt_parser import extract_txt_text
from services.ingestion.parsers.html_parser import extract_html_text

from services.ingestion.preprocessing.text_cleaner import clean_text
from services.ingestion.preprocessing.layout_normalizer import normalize_layout
from services.ingestion.preprocessing.structure_fix import fix_structure
from services.ingestion.preprocessing.date_normalizer import normalize_dates
from services.ingestion.preprocessing.currency_normalizer import normalize_currencies
from services.ingestion.preprocessing.numeric_normalizer import normalize_numbers


PARSERS = {
    ".pdf": extract_pdf_text,
    ".docx": extract_docx_text,
    ".doc": extract_docx_text,
    ".xlsx": extract_xlsx_text,
    ".xls": extract_xlsx_text,
    ".csv": extract_csv_text,
    ".txt": extract_txt_text,
    ".html": extract_html_text,
    ".htm": extract_html_text,
}


def preprocess_text(text: str) -> str:
    """Apply the full preprocessing pipeline to extracted text."""
    text = normalize_layout(text)
    text = fix_structure(text)
    text = clean_text(text)
    text = normalize_dates(text)
    text = normalize_currencies(text)
    text = normalize_numbers(text)
    return text


def extract_text(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    parser = PARSERS.get(extension)

    if parser is None:
        raise ValueError(f"Unsupported file type: {extension}")

    raw_text = parser(file_path)
    return preprocess_text(raw_text)
