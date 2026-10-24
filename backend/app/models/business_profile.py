from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class BusinessProfile(Base):
    """The user's business portfolio. Kept separate from User (credentials).

    One profile per user (unique user_id). Contextual input for future AI
    recommendations (see app/services/business_context.py).

    `description` and `business_model` are nullable at the DATABASE level only so
    that rows created before they existed migrate safely. The API requires both,
    and `onboarding_completed` is false until they are filled in.
    """

    __tablename__ = "business_profiles"
    __table_args__ = (
        CheckConstraint(
            "business_model IS NULL OR business_model IN ('product', 'service', 'both')",
            name="business_model_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    business_name: Mapped[str] = mapped_column(String(200))  # brand / entity name
    industry: Mapped[str] = mapped_column(String(100))  # business domain / industry category
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_model: Mapped[str | None] = mapped_column(String(20), nullable=True)  # product|service|both
    # List of channel codes, e.g. ["own_website", "social_commerce"]. JSON works on PostgreSQL and SQLite.
    sales_channels: Mapped[list[str]] = mapped_column(JSON, default=list)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)  # location / target market
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)  # marketing goals
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="business_profile")
