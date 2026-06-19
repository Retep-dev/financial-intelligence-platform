import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.postgres.base import Base


class ChunkStatus(str, PyEnum):
    PENDING = "pending"
    EMBEDDED = "embedded"
    FAILED = "failed"


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    section: Mapped[str] = mapped_column(
        String,
        nullable=True
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    embedding_id: Mapped[str] = mapped_column(
        String,
        nullable=True,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String,
        default=ChunkStatus.PENDING.value,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
