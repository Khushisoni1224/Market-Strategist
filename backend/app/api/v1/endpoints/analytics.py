"""Analytics API endpoints."""

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.analytics import AnalyticsSnapshotResponse
from app.services.analytics_snapshot import get_analytics_snapshot


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


@router.get(
    "/summary",
    response_model=AnalyticsSnapshotResponse,
    summary="Get combined business analytics",
    description=(
        "Returns a summary of customer feedback and marketing "
        "performance for the authenticated user's business."
    ),
)
def get_analytics_summary(
    current_user: CurrentUser,
    db: DbSession,
) -> AnalyticsSnapshotResponse:
    """Return analytics belonging only to the authenticated user."""
    snapshot = get_analytics_snapshot(
        db=db,
        user_id=current_user.id,
    )

    return AnalyticsSnapshotResponse(**snapshot)