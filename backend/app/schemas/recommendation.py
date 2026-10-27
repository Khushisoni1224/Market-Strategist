"""Request/response shapes for recommendations (the contract Member 1 builds against)."""
from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, model_validator

from app.models.recommendation import RecommendationStatus  # re-exported on purpose

__all__ = [
    "RecommendationStatus", "UtcDatetime", "OutcomeCreate", "OutcomeOut",
    "RecommendationUpdate", "RecommendationOut",
]


def _to_utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


UtcDatetime = Annotated[datetime, PlainSerializer(_to_utc_iso, return_type=str)]


class OutcomeCreate(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)
    reach: int | None = Field(default=None, ge=0)     # None = not recorded
    clicks: int | None = Field(default=None, ge=0)
    orders: int | None = Field(default=None, ge=0)


class OutcomeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    notes: str | None
    reach: int | None
    clicks: int | None
    orders: int | None
    recorded_at: UtcDatetime


class RecommendationUpdate(BaseModel):
    """Body of PATCH. Send only what the seller changed."""
    status: RecommendationStatus | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    suggested_content: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.status is None and self.title is None and self.suggested_content is None:
            raise ValueError("Provide at least one of: status, title, suggested_content")
        return self


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    strategy_run_id: int
    target_product_id: int | None
    title: str
    action_type: str
    priority: int
    score: float | None
    score_interpretation: str
    reasoning_summary: str
    supporting_evidence: list[str]
    suggested_content: str | None
    data_gaps: list[str]
    caveats: list[str]
    status: RecommendationStatus
    created_at: UtcDatetime
    updated_at: UtcDatetime
    outcomes: list[OutcomeOut] = []
