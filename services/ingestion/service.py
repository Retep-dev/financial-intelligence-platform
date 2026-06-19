from pathlib import Path
from datetime import datetime

from db.postgres.models.document import Document, DocumentStatus
from db.postgres.session import SessionLocal


def create_document_record(
    original_filename: str,
    file_path: str,
    analyst_id: str = None,
    source: str = "manual_upload"
):

    db = SessionLocal()

    try:
        document = Document(
            file_name=original_filename,
            stored_file_name=Path(file_path).name,
            file_path=file_path,
            document_type=Path(original_filename).suffix,
            source=source,
            analyst_id=analyst_id,
            status=DocumentStatus.PENDING.value,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    finally:
        db.close()


def update_document_status(
    document_id: str,
    status: DocumentStatus,
    page_count: int = None
):
    db = SessionLocal()

    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if document:
            document.status = status.value
            document.updated_at = datetime.utcnow()

            if page_count is not None:
                document.page_count = page_count

            db.commit()
            db.refresh(document)

        return document

    finally:
        db.close()
