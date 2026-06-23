from financial_intelligence_platform.db.postgres.database import SessionLocal

from financial_intelligence_platform.db.postgres.models.document import Document

from financial_intelligence_platform.services.ingestion.parsers.parser_router import extract_text
from financial_intelligence_platform.services.chunking.chunker import split_into_chunks
from financial_intelligence_platform.services.chunking.chunk_repository import save_chunks


db = SessionLocal()


document = (
    db.query(Document)
    .filter(Document.document_type == ".pdf")
    .first()
)

if not document:
    print("No document found")
    exit()

text = extract_text(document.file_path)

chunks = split_into_chunks(
    text=text,
    document_id=document.id
)

save_chunks(
    db=db,
    document_id=document.id,
    chunks=chunks
)

print(f"Saved {len(chunks)} chunks")
