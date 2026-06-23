"""Check if Tesseract OCR is available and test it on a PDF."""
import sys

from financial_intelligence_platform.services.ingestion.preprocessing.ocr import is_tesseract_available, ocr_pdf


def main():
    print(f"Tesseract available: {is_tesseract_available()}")

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"\nTrying OCR on: {file_path}")
        try:
            text = ocr_pdf(file_path, min_text_length=0)
            print(f"Extracted {len(text)} characters")
            print("Sample:")
            print(text[:1000])
        except Exception as e:
            print(f"OCR failed: {e}")


if __name__ == "__main__":
    main()
