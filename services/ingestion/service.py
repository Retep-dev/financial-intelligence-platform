from pathlib import Path
from datetime import datetime

from db.postgres.models import Document
from db.postgres.session import SessionLocal


def create_document_record(original_filename: str, file_path: str):

    db = SessionLocal()

    try:
        document = Document(
            file_name=original_filename,
            stored_file_name=Path(file_path).name,
            file_path=file_path,
            document_type=Path(original_filename).suffix,
            source="manual_upload",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    finally:
        db.close()
