"""Authenticated API endpoints for marketing performance data."""

from datetime import date

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select

from app.core.dependencies import CurrentUser, DbSession
from app.models.marketing_import import MarketingImport
from app.models.marketing_performance import MarketingPerformance
from app.schemas.marketing import (
    MarketingImportListResponse,
    MarketingImportRead,
    MarketingImportResult,
    MarketingListResponse,
    MarketingPerformanceRead,
)
from app.services.marketing_import import (
    MAX_FILE_SIZE,
    MarketingImportError,
    process_marketing_csv,
)
from app.services.marketing_metrics import calculate_marketing_rates


router = APIRouter(prefix="/marketing", tags=["marketing"])


@router.post(
    "/import",
    response_model=MarketingImportResult,
    status_code=status.HTTP_201_CREATED,
)
async def import_marketing_csv(
    current_user: CurrentUser,
    db: DbSession,
    file: UploadFile = File(...),
):
    """Upload and process a marketing performance CSV."""

    if file.filename and not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a CSV file.",
        )

    try:
        # Read at most one byte beyond the allowed size.
        file_bytes = await file.read(MAX_FILE_SIZE + 1)

        result = process_marketing_csv(
            db=db,
            user_id=current_user.id,
            filename=file.filename or "marketing.csv",
            file_bytes=file_bytes,
        )

        return result

    except MarketingImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()


@router.get("", response_model=MarketingListResponse)
def list_marketing_performance(
    current_user: CurrentUser,
    db: DbSession,
    platform: str | None = Query(default=None, min_length=1, max_length=100),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """List the authenticated user's marketing records."""

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must not be later than end_date.",
        )

    conditions = [
        MarketingPerformance.user_id == current_user.id,
    ]

    if platform is not None:
        conditions.append(
            func.lower(MarketingPerformance.platform)
            == platform.strip().lower()
        )

    if start_date is not None:
        conditions.append(
            MarketingPerformance.content_date >= start_date
        )

    if end_date is not None:
        conditions.append(
            MarketingPerformance.content_date <= end_date
        )

    total = db.scalar(
        select(func.count())
        .select_from(MarketingPerformance)
        .where(*conditions)
    ) or 0

    statement = (
        select(MarketingPerformance)
        .where(*conditions)
        .order_by(
            MarketingPerformance.content_date.desc(),
            MarketingPerformance.id.desc(),
        )
        .offset(skip)
        .limit(limit)
    )

    records = db.scalars(statement).all()

    items = []

    for record in records:
        rates = calculate_marketing_rates(
            reach=record.reach,
            impressions=record.impressions,
            clicks=record.clicks,
            likes=record.likes,
            comments=record.comments,
            shares=record.shares,
            conversions=record.conversions,
        )

        item = {
            "id": record.id,
            "user_id": record.user_id,
            "marketing_import_id": record.marketing_import_id,
            "content_date": record.content_date,
            "content_id": record.content_id,
            "platform": record.platform,
            "content_type": record.content_type,
            "reach": record.reach,
            "impressions": record.impressions,
            "clicks": record.clicks,
            "likes": record.likes,
            "comments": record.comments,
            "shares": record.shares,
            "conversions": record.conversions,
            "created_at": record.created_at,
            **rates,
        }

        items.append(item)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }


@router.get(
    "/imports",
    response_model=MarketingImportListResponse,
)
def list_marketing_imports(
    current_user: CurrentUser,
    db: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """List only the authenticated user's marketing import history."""

    total = db.scalar(
        select(func.count())
        .select_from(MarketingImport)
        .where(MarketingImport.user_id == current_user.id)
    ) or 0

    statement = (
        select(MarketingImport)
        .where(MarketingImport.user_id == current_user.id)
        .order_by(MarketingImport.id.desc())
        .offset(skip)
        .limit(limit)
    )

    records = list(db.scalars(statement).all())

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": records,
    }