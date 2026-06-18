import fitz  # PyMuPDF


def extract_pdf_text(file_path: str) -> str:
    doc = fitz.open(file_path)

    text_blocks = []

    for page in doc:
        blocks = page.get_text("blocks")  # IMPORTANT upgrade

        for b in blocks:
            text_blocks.append(b[4])  # text content only

    return "\n".join(text_blocks)
