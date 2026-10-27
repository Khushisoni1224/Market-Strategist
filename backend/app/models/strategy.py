"""StrategyRun model. One run = one click on "Generate strategy"."""
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    """UTC time without tzinfo (SQLite friendly). The API adds the 'Z' suffix."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class StrategyRun(Base):
    __tablename__ = "strategy_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    llm_provider: Mapped[str] = mapped_column(String(50))
    used_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    data_warnings: Mapped[list] = mapped_column(JSON, default=list)
    weights_used: Mapped[dict] = mapped_column(JSON, default=dict)

    recommendations: Mapped[list["Recommendation"]] = relationship(  # noqa: F821
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="Recommendation.priority",
    )
