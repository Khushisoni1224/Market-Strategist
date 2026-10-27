"""Database model for imported marketing performance metrics."""

from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MarketingPerformance(Base):
    """Stores marketing performance metrics for an individual content item."""

    __tablename__ = "marketing_performance"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "content_date",
            "content_id",
            name="user_date_content_unique",
        ),
        CheckConstraint(
            "reach IS NULL OR reach >= 0",
            name="reach_non_negative",
        ),
        CheckConstraint(
            "impressions IS NULL OR impressions >= 0",
            name="impressions_non_negative",
        ),
        CheckConstraint(
            "clicks IS NULL OR clicks >= 0",
            name="clicks_non_negative",
        ),
        CheckConstraint(
            "likes IS NULL OR likes >= 0",
            name="likes_non_negative",
        ),
        CheckConstraint(
            "comments IS NULL OR comments >= 0",
            name="comments_non_negative",
        ),
        CheckConstraint(
            "shares IS NULL OR shares >= 0",
            name="shares_non_negative",
        ),
        CheckConstraint(
            "conversions IS NULL OR conversions >= 0",
            name="conversions_non_negative",
        ),
        Index(
            "ix_marketing_performance_user_date",
            "user_id",
            "content_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    marketing_import_id: Mapped[int] = mapped_column(
        ForeignKey("marketing_imports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    content_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    platform: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reach: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    impressions: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    clicks: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    likes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    comments: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    shares: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    conversions: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )