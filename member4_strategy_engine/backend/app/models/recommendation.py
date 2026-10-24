"""Recommendation and Outcome models."""
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.strategy import utcnow


class RecommendationStatus(str, Enum):
    """Agree on this list with Member 1 (frontend) before changing it."""
    proposed = "proposed"
    approved = "approved"
    edited = "edited"
    ignored = "ignored"
    executed = "executed"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    strategy_run_id: Mapped[int] = mapped_column(ForeignKey("strategy_runs.id"), index=True)
    owner_id: Mapped[int] = mapped_column(Integer, index=True)
    target_product_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    action_type: Mapped[str] = mapped_column(String(50))
    priority: Mapped[int] = mapped_column(Integer)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_interpretation: Mapped[str] = mapped_column(String(30))
    reasoning_summary: Mapped[str] = mapped_column(Text)
    supporting_evidence: Mapped[list] = mapped_column(JSON, default=list)
    suggested_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_gaps: Mapped[list] = mapped_column(JSON, default=list)
    caveats: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default=RecommendationStatus.proposed.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    run: Mapped["StrategyRun"] = relationship(back_populates="recommendations")  # noqa: F821
    outcomes: Mapped[list["Outcome"]] = relationship(
        back_populates="recommendation", cascade="all, delete-orphan", order_by="Outcome.id"
    )


class Outcome(Base):
    """Result the seller chooses to record. None = 'not recorded' (never 0)."""
    __tablename__ = "recommendation_outcomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("recommendations.id"), index=True)
    owner_id: Mapped[int] = mapped_column(Integer, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    clicks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    orders: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    recommendation: Mapped["Recommendation"] = relationship(back_populates="outcomes")
