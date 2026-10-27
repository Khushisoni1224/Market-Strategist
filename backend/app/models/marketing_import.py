"""Database model for marketing performance CSV import history."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MarketingImport(Base):
    """Tracks the processing status and results of a marketing CSV import."""

    __tablename__ = "marketing_imports"

    __table_args__ = (
        CheckConstraint(
            "status IN ('processing', 'completed', 'failed')",
            name="status_valid",
        ),
        CheckConstraint("total_rows >= 0", name="total_rows_non_negative"),
        CheckConstraint("saved_rows >= 0", name="saved_rows_non_negative"),
        CheckConstraint("updated_rows >= 0", name="updated_rows_non_negative"),
        CheckConstraint("invalid_rows >= 0", name="invalid_rows_non_negative"),
        Index("ix_marketing_imports_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="processing",
    )

    total_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    saved_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    updated_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    invalid_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )