"""Calculate marketing performance rates safely."""

from typing import TypedDict


class MarketingRates(TypedDict):
    """Calculated marketing rates expressed as percentages."""

    click_through_rate: float | None
    engagement_rate: float | None
    conversion_rate: float | None


def _calculate_rate(
    numerator: int | None,
    denominator: int | None,
) -> float | None:
    """Calculate a percentage when both values are valid."""
    if numerator is None or denominator is None:
        return None

    if denominator <= 0:
        return None

    return round((numerator / denominator) * 100, 2)


def calculate_marketing_rates(
    *,
    reach: int | None,
    impressions: int | None,
    clicks: int | None,
    likes: int | None,
    comments: int | None,
    shares: int | None,
    conversions: int | None,
) -> MarketingRates:
    """
    Calculate CTR, engagement rate, and conversion rate.

    Missing inputs or zero denominators produce None rather than
    misleading percentages.

    Engagement rate is calculated only when reach, likes, comments,
    and shares are all available.
    """
    click_through_rate = _calculate_rate(
        clicks,
        impressions,
    )

    conversion_rate = _calculate_rate(
        conversions,
        clicks,
    )

    engagement_rate: float | None = None

    if (
        reach is not None
        and reach > 0
        and likes is not None
        and comments is not None
        and shares is not None
    ):
        total_engagements = likes + comments + shares

        engagement_rate = _calculate_rate(
            total_engagements,
            reach,
        )

    return {
        "click_through_rate": click_through_rate,
        "engagement_rate": engagement_rate,
        "conversion_rate": conversion_rate,
    }