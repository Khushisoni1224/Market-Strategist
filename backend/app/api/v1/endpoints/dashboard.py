"""GET /dashboard/summary  (coordinate the final shape with Member 1 and the others)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.strategy import DashboardSummary
from app.services import recommendation_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_current_user_id),
):
    return recommendation_service.dashboard_summary(db, owner_id)
