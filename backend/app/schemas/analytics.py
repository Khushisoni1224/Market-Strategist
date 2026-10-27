"""Response schemas for combined business analytics."""

from pydantic import BaseModel, ConfigDict, Field


class SentimentCounts(BaseModel):
    """Number of reviews in each sentiment category."""

    Positive: int = Field(ge=0)
    Neutral: int = Field(ge=0)
    Negative: int = Field(ge=0)


class SentimentPercentages(BaseModel):
    """Percentage of reviews in each sentiment category."""

    Positive: float = Field(ge=0, le=100)
    Neutral: float = Field(ge=0, le=100)
    Negative: float = Field(ge=0, le=100)


class ComplaintThemeCount(BaseModel):
    """Number of reviews associated with a complaint theme."""

    theme: str
    count: int = Field(ge=0)


class FeedbackAnalytics(BaseModel):
    """Summary of customer feedback."""

    total_feedback: int = Field(ge=0)
    average_rating: float | None = None
    sentiment_counts: SentimentCounts
    sentiment_percentages: SentimentPercentages
    complaint_themes: list[ComplaintThemeCount]


class MarketingMetricTotals(BaseModel):
    """Aggregated marketing metrics."""

    reach: int | None = Field(default=None, ge=0)
    impressions: int | None = Field(default=None, ge=0)
    clicks: int | None = Field(default=None, ge=0)
    likes: int | None = Field(default=None, ge=0)
    comments: int | None = Field(default=None, ge=0)
    shares: int | None = Field(default=None, ge=0)
    conversions: int | None = Field(default=None, ge=0)


class MarketingAnalytics(BaseModel):
    """Summary of marketing performance."""

    total_posts: int = Field(ge=0)
    metric_totals: MarketingMetricTotals
    click_through_rate: float | None = Field(default=None, ge=0)
    engagement_rate: float | None = Field(default=None, ge=0)
    conversion_rate: float | None = Field(default=None, ge=0)


class AnalyticsSnapshotResponse(BaseModel):
    """Combined feedback and marketing analytics."""

    model_config = ConfigDict(from_attributes=True)

    feedback: FeedbackAnalytics
    marketing: MarketingAnalytics