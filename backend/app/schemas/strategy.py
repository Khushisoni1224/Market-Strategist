"""Strategy request/response shapes + the shape we REQUIRE from the AI."""
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.recommendation import RecommendationOut, UtcDatetime


# ------------------------------------------------------------------ API
class StrategyGenerateRequest(BaseModel):
    max_recommendations: int | None = Field(default=None, ge=1, le=10)


class StrategyRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: UtcDatetime
    llm_provider: str
    used_fallback: bool
    data_warnings: list[str]
    weights_used: dict[str, float]
    recommendations: list[RecommendationOut]


class StrategyRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: UtcDatetime
    llm_provider: str
    used_fallback: bool
    data_warnings: list[str]


class DashboardSummary(BaseModel):
    latest_run_id: int | None
    latest_run_at: UtcDatetime | None
    total_runs: int
    status_counts: dict[str, int]
    top_recommendations: list[RecommendationOut]


# ------------------------------------------------------------------ AI output contract
class LLMRecommendation(BaseModel):
    product_id: int
    title: str = Field(min_length=1, max_length=200)
    reasoning_summary: str = Field(min_length=1, max_length=1500)
    suggested_content: str | None = Field(default=None, max_length=1500)
    evidence_used: list[str] = Field(default_factory=list, max_length=10)
    caveats: list[str] = Field(default_factory=list, max_length=10)


class LLMOutput(BaseModel):
    recommendations: list[LLMRecommendation] = Field(min_length=1)
