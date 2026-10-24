"""GET /recommendations, GET/PATCH /recommendations/{id}, POST /recommendations/{id}/outcome"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.recommendation import (
    OutcomeCreate,
    RecommendationOut,
    RecommendationStatus,
    RecommendationUpdate,
)
from app.services import recommendation_service
from app.services.errors import NotFoundError, PersistenceError

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationOut])
def list_recommendations(
    status: RecommendationStatus | None = None,
    run_id: int | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_current_user_id),
):
    return recommendation_service.list_recommendations(db, owner_id, status, run_id, limit, offset)


@router.get("/{recommendation_id}", response_model=RecommendationOut)
def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_current_user_id),
):
    try:
        return recommendation_service.get_recommendation(db, owner_id, recommendation_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{recommendation_id}", response_model=RecommendationOut)
def update_recommendation(
    recommendation_id: int,
    payload: RecommendationUpdate,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_current_user_id),
):
    try:
        changes = payload.model_dump(exclude_unset=True)
        return recommendation_service.update_recommendation(db, owner_id, recommendation_id, changes)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{recommendation_id}/outcome", response_model=RecommendationOut, status_code=201)
def record_outcome(
    recommendation_id: int,
    payload: OutcomeCreate,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_current_user_id),
):
    try:
        return recommendation_service.record_outcome(
            db, owner_id, recommendation_id, payload.model_dump()
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
