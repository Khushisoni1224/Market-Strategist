"""POST /strategy/generate, GET /strategy/runs, GET /strategy/runs/{run_id}"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id, get_evidence_source, get_llm_provider
from app.db.session import get_db
from app.schemas.strategy import StrategyGenerateRequest, StrategyRunOut, StrategyRunSummary
from app.services import recommendation_service, strategy_service
from app.services.errors import NoDataError, NotFoundError, PersistenceError

router = APIRouter(prefix="/strategy", tags=["strategy"])


@router.post("/generate", response_model=StrategyRunOut, status_code=201)
def generate_strategy(
    payload: StrategyGenerateRequest | None = None,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_current_user_id),
    source=Depends(get_evidence_source),
    provider=Depends(get_llm_provider),
):
    max_recs = payload.max_recommendations if payload else None
    try:
        return strategy_service.generate_strategy(db, owner_id, source, provider, max_recs)
    except NoDataError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/runs", response_model=list[StrategyRunSummary])
def list_runs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_current_user_id),
):
    return recommendation_service.list_runs(db, owner_id, limit, offset)


@router.get("/runs/{run_id}", response_model=StrategyRunOut)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_current_user_id),
):
    try:
        return recommendation_service.get_run(db, owner_id, run_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
