"""Read/update recommendations and runs. EVERY query is filtered by owner_id.

If something belongs to another seller we answer "not found" (never reveal it exists).
"""
import logging
from enum import Enum

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.recommendation import Outcome, Recommendation, RecommendationStatus
from app.models.strategy import StrategyRun, utcnow
from app.services.errors import NotFoundError, PersistenceError

logger = logging.getLogger(__name__)


def _commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database commit failed (%s)", type(exc).__name__)
        raise PersistenceError("Could not save your changes. Please try again.") from exc


# ------------------------------------------------------------------ runs
def list_runs(db: Session, owner_id: int, limit: int = 20, offset: int = 0) -> list:
    stmt = (
        select(StrategyRun)
        .where(StrategyRun.owner_id == owner_id)
        .order_by(StrategyRun.created_at.desc(), StrategyRun.id.desc())
        .limit(limit).offset(offset)
    )
    return list(db.scalars(stmt).all())


def get_run(db: Session, owner_id: int, run_id: int) -> StrategyRun:
    run = db.scalar(select(StrategyRun).where(StrategyRun.id == run_id, StrategyRun.owner_id == owner_id))
    if run is None:
        raise NotFoundError("Strategy run not found.")
    return run


# ------------------------------------------------------------------ recommendations
def list_recommendations(
    db: Session, owner_id: int, status: RecommendationStatus | None = None,
    run_id: int | None = None, limit: int = 50, offset: int = 0,
) -> list:
    stmt = select(Recommendation).where(Recommendation.owner_id == owner_id)
    if status is not None:
        stmt = stmt.where(Recommendation.status == status.value)
    if run_id is not None:
        stmt = stmt.where(Recommendation.strategy_run_id == run_id)
    stmt = stmt.order_by(Recommendation.strategy_run_id.desc(), Recommendation.priority.asc())
    return list(db.scalars(stmt.limit(limit).offset(offset)).all())


def get_recommendation(db: Session, owner_id: int, recommendation_id: int) -> Recommendation:
    rec = db.scalar(
        select(Recommendation).where(
            Recommendation.id == recommendation_id, Recommendation.owner_id == owner_id
        )
    )
    if rec is None:
        raise NotFoundError("Recommendation not found.")
    return rec


def update_recommendation(db: Session, owner_id: int, recommendation_id: int, changes: dict) -> Recommendation:
    rec = get_recommendation(db, owner_id, recommendation_id)
    edited = False

    title = changes.get("title")
    if title is not None and title != rec.title:
        rec.title = title
        edited = True
    content = changes.get("suggested_content")
    if content is not None and content != rec.suggested_content:
        rec.suggested_content = content
        edited = True

    status = changes.get("status")
    if status is not None:
        rec.status = status.value if isinstance(status, Enum) else status
    elif edited:
        rec.status = RecommendationStatus.edited.value

    rec.updated_at = utcnow()
    _commit(db)
    db.refresh(rec)
    return rec


def record_outcome(db: Session, owner_id: int, recommendation_id: int, data: dict) -> Recommendation:
    rec = get_recommendation(db, owner_id, recommendation_id)
    rec.outcomes.append(Outcome(
        owner_id=owner_id,
        notes=data.get("notes"),
        reach=data.get("reach"),
        clicks=data.get("clicks"),
        orders=data.get("orders"),
    ))
    rec.status = RecommendationStatus.executed.value
    rec.updated_at = utcnow()
    _commit(db)
    db.refresh(rec)
    return rec


# ------------------------------------------------------------------ dashboard
def dashboard_summary(db: Session, owner_id: int) -> dict:
    latest = db.scalar(
        select(StrategyRun).where(StrategyRun.owner_id == owner_id)
        .order_by(StrategyRun.created_at.desc(), StrategyRun.id.desc()).limit(1)
    )
    total_runs = db.scalar(
        select(func.count()).select_from(StrategyRun).where(StrategyRun.owner_id == owner_id)
    ) or 0

    counts = {s.value: 0 for s in RecommendationStatus}
    rows = db.execute(
        select(Recommendation.status, func.count())
        .where(Recommendation.owner_id == owner_id)
        .group_by(Recommendation.status)
    ).all()
    for status, count in rows:
        counts[status] = count

    top = []
    if latest is not None:
        top = list(db.scalars(
            select(Recommendation)
            .where(Recommendation.strategy_run_id == latest.id, Recommendation.owner_id == owner_id)
            .order_by(Recommendation.priority.asc()).limit(3)
        ).all())

    return {
        "latest_run_id": latest.id if latest else None,
        "latest_run_at": latest.created_at if latest else None,
        "total_runs": total_runs,
        "status_counts": counts,
        "top_recommendations": top,
    }
