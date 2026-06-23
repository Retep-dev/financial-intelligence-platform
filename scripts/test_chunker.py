from financial_intelligence_platform.db.postgres.models import Document
from financial_intelligence_platform.db.postgres.session import SessionLocal

from financial_intelligence_platform.services.ingestion.parsers.parser_router import extract_text
from financial_intelligence_platform.services.chunking.chunker import split_into_chunks

db = SessionLocal()

doc = (
    db.query(Document)
    .filter(Document.document_type == ".pdf")
    .first()
)

text = extract_text(doc.file_path)

print("\n===== RAW TEXT PREVIEW =====\n")
print(repr(text[:1000]))

chunks = split_into_chunks(
    text,
    document_id=doc.id
)

print(f"\nTotal chunks: {len(chunks)}")

for i, chunk in enumerate(chunks[:5]):
    print(f"\n--- CHUNK {i+1} ---\n")
    print(chunk["text"][:500])
