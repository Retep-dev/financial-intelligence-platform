from services.ingestion.preprocessing.text_cleaner import clean_text


def extract_txt_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    return clean_text(raw)
