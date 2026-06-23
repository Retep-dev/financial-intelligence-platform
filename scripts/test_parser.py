from financial_intelligence_platform.db.postgres.models import Document
from financial_intelligence_platform.db.postgres.session import SessionLocal

from financial_intelligence_platform.services.ingestion.parsers.parser_router import extract_text


db = SessionLocal()

doc = db.query(Document).filter(Document.document_type == ".pdf").first()

if not doc:
    print("No PDF found. Upload a PDF first.")
    exit()

text = extract_text(doc.file_path)

print("\n--- EXTRACTED TEXT PREVIEW ---\n")
print(text[:1000])
