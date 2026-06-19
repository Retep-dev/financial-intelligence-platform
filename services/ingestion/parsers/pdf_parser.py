import fitz


def extract_pdf_text(file_path: str) -> str:

    doc = fitz.open(file_path)

    full_text = []

    for page in doc:

        blocks = page.get_text("blocks")

        # sort reading order
        blocks.sort(key=lambda b: (b[1], b[0]))

        page_text = []

        for b in blocks:
            text = b[4].strip()

            # FIX: merge broken lines inside blocks
            lines = text.split("\n")
            merged = " ".join(line.strip() for line in lines if line.strip())

            page_text.append(merged)

        full_text.append(" ".join(page_text))

    return "\n".join(full_text)
