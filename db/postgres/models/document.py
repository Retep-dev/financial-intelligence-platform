import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from db.postgres.base import Base


class DocumentStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    file_name: Mapped[str] = mapped_column(String)

    stored_file_name: Mapped[str] = mapped_column(String)

    file_path: Mapped[str] = mapped_column(String)

    document_type: Mapped[str] = mapped_column(String)

    source: Mapped[str] = mapped_column(
        String,
        default="manual_upload"
    )

    analyst_id: Mapped[str] = mapped_column(
        String,
        nullable=True
    )

    page_count: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String,
        default=DocumentStatus.PENDING.value,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
