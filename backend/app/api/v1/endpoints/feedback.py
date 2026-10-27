"""Authenticated API endpoints for customer feedback and CSV imports."""

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select

from app.core.dependencies import CurrentUser, DbSession
from app.models.customer_feedback import CustomerFeedback
from app.models.feedback_import import FeedbackImport
from app.schemas.feedback import (
    FeedbackImportListResponse,
    FeedbackImportRead,
    FeedbackImportResult,
    FeedbackListResponse,
    FeedbackRead,
)
from app.services.feedback_import import (
    MAX_FILE_SIZE,
    FeedbackImportError,
    process_feedback_csv,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post(
    "/import",
    response_model=FeedbackImportResult,
    status_code=status.HTTP_201_CREATED,
)
async def import_feedback_csv(
    current_user: CurrentUser,
    db: DbSession,
    file: UploadFile = File(...),
):
    """Upload a CSV, analyze its reviews, and save the results."""

    if file.filename and not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a CSV file.",
        )

    try:
        # Read at most 1 byte beyond the limit to detect oversized files.
        file_bytes = await file.read(MAX_FILE_SIZE + 1)

        result = process_feedback_csv(
            db=db,
            user_id=current_user.id,
            filename=file.filename or "feedback.csv",
            file_bytes=file_bytes,
        )

        return result

    except FeedbackImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()


@router.get("", response_model=FeedbackListResponse)
def list_feedback(
    current_user: CurrentUser,
    db: DbSession,
    sentiment: str | None = Query(
        default=None,
        pattern="^(Positive|Neutral|Negative)$",
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Return the authenticated user's feedback with pagination."""

    conditions = [CustomerFeedback.user_id == current_user.id]

    if sentiment is not None:
        conditions.append(CustomerFeedback.sentiment == sentiment)

    total = db.scalar(
        select(func.count())
        .select_from(CustomerFeedback)
        .where(*conditions)
    ) or 0

    statement = (
        select(CustomerFeedback)
        .where(*conditions)
        .order_by(CustomerFeedback.id.desc())
        .offset(skip)
        .limit(limit)
    )

    items = list(db.scalars(statement).all())

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }


@router.get(
    "/imports",
    response_model=FeedbackImportListResponse,
)
def list_feedback_imports(
    current_user: CurrentUser,
    db: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Return only the authenticated user's feedback import history."""

    total = db.scalar(
        select(func.count())
        .select_from(FeedbackImport)
        .where(FeedbackImport.user_id == current_user.id)
    ) or 0

    statement = (
        select(FeedbackImport)
        .where(FeedbackImport.user_id == current_user.id)
        .order_by(FeedbackImport.id.desc())
        .offset(skip)
        .limit(limit)
    )

    items = list(db.scalars(statement).all())

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }