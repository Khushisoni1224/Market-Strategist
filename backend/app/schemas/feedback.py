from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SentimentType = Literal["Positive", "Neutral", "Negative"]


class FeedbackRead(BaseModel):
    """Response schema for one customer feedback record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    feedback_import_id: int
    review_text: str
    rating: int | None
    sentiment: SentimentType
    sentiment_score: float
    themes: list[str]
    product_id: int | None
    created_at: datetime


class FeedbackImportRead(BaseModel):
    """Response schema describing a feedback CSV import."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    filename: str
    status: Literal["processing", "completed", "failed"]
    total_rows: int
    saved_rows: int
    failed_rows: int
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None


class FeedbackListResponse(BaseModel):
    """Paginated list of customer feedback."""

    total: int = Field(ge=0)
    skip: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    items: list[FeedbackRead]


class FeedbackImportListResponse(BaseModel):
    """Paginated list of feedback import history."""

    total: int = Field(ge=0)
    skip: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    items: list[FeedbackImportRead]


class FeedbackImportResult(BaseModel):
    """Summary returned after importing a CSV file."""

    import_id: int
    filename: str
    status: Literal["completed"]
    total_rows: int
    saved_rows: int
    failed_rows: int