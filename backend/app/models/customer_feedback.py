"""Database model for imported customer reviews and sentiment analysis."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CustomerFeedback(Base):
    """Stores a customer review and its precomputed analysis."""

    __tablename__ = "customer_feedback"

    __table_args__ = (
        CheckConstraint(
            "rating IS NULL OR rating BETWEEN 1 AND 5",
            name="rating_valid",
        ),
        CheckConstraint(
            "sentiment IN ('Positive', 'Neutral', 'Negative')",
            name="sentiment_valid",
        ),
        CheckConstraint(
            "sentiment_score BETWEEN -1 AND 1",
            name="sentiment_score_valid",
        ),
        Index(
            "ix_customer_feedback_user_sentiment",
            "user_id",
            "sentiment",
        ),
        Index(
            "ix_customer_feedback_user_created",
            "user_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    feedback_import_id: Mapped[int] = mapped_column(
        ForeignKey("feedback_imports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    review_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    sentiment: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sentiment_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    themes: Mapped[list[Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )