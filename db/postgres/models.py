import uuid

from datetime import datetime

from sqlalchemy import String
from sqlalchemy import DateTime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db.postgres.base import Base


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

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
