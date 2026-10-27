"""Pydantic schemas for marketing performance and imports."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ImportStatus = Literal["processing", "completed", "failed"]


class MarketingPerformanceRead(BaseModel):
    """Marketing performance record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    marketing_import_id: int
    content_date: date
    content_id: str
    platform: str | None
    content_type: str | None

    reach: int | None
    impressions: int | None
    clicks: int | None
    likes: int | None
    comments: int | None
    shares: int | None
    conversions: int | None

    created_at: datetime

    click_through_rate: float | None = None
    engagement_rate: float | None = None
    conversion_rate: float | None = None


class MarketingImportRead(BaseModel):
    """One marketing CSV import-history record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    filename: str
    status: ImportStatus
    total_rows: int
    saved_rows: int
    updated_rows: int
    invalid_rows: int
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None


class MarketingListResponse(BaseModel):
    """Paginated marketing performance records."""

    total: int = Field(ge=0)
    skip: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    items: list[MarketingPerformanceRead]


class MarketingImportListResponse(BaseModel):
    """Paginated marketing import history."""

    total: int = Field(ge=0)
    skip: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    items: list[MarketingImportRead]


class MarketingImportResult(BaseModel):
    """Summary returned after importing a marketing CSV."""

    import_id: int
    filename: str
    status: Literal["completed"]
    total_rows: int
    saved_rows: int
    updated_rows: int
    invalid_rows: int