import io
from typing import Optional

import fitz
from PIL import Image


def is_tesseract_available() -> bool:
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def ocr_page(page: fitz.Page, dpi: int = 200) -> str:
    """OCR a single PDF page using Tesseract."""
    if not is_tesseract_available():
        raise RuntimeError("Tesseract OCR is not available")

    import pytesseract

    pix = page.get_pixmap(dpi=dpi)
    img = Image.open(io.BytesIO(pix.tobytes("png")))

    text = pytesseract.image_to_string(img)
    return text.strip()


def ocr_pdf(file_path: str, min_text_length: int = 100) -> Optional[str]:
    """OCR a PDF if the extracted text is too short or missing."""
    if not is_tesseract_available():
        return None

    doc = fitz.open(file_path)

    pages_text = []
    for page in doc:
        text = ocr_page(page)
        if text:
            pages_text.append(text)

    doc.close()

    combined = "\n".join(pages_text)
    return combined if len(combined) >= min_text_length else None
