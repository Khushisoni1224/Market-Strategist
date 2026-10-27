"""Build a user-specific analytics summary from stored data."""

from collections import Counter

from sqlalchemy.orm import Session

from app.models.customer_feedback import CustomerFeedback
from app.models.marketing_performance import MarketingPerformance
from app.services.marketing_metrics import calculate_marketing_rates


def _calculate_average_rating(
    feedback_rows: list[CustomerFeedback],
) -> float | None:
    """Calculate the average of available customer ratings."""
    ratings = [
        row.rating
        for row in feedback_rows
        if row.rating is not None
    ]

    if not ratings:
        return None

    return round(sum(ratings) / len(ratings), 2)


def _aggregate_metric(
    marketing_rows: list[MarketingPerformance],
    field_name: str,
) -> int | None:
    """Sum a marketing metric only when all its values are available."""
    if not marketing_rows:
        return None

    values = [
        getattr(row, field_name)
        for row in marketing_rows
    ]

    # Avoid presenting an incomplete sum as a complete total.
    if any(value is None for value in values):
        return None

    return sum(values)


def get_analytics_snapshot(
    db: Session,
    user_id: int,
) -> dict:
    """
    Return a combined feedback and marketing summary for one user.

    All database queries are scoped to the supplied user ID.
    """
    feedback_rows = (
        db.query(CustomerFeedback)
        .filter(CustomerFeedback.user_id == user_id)
        .all()
    )

    marketing_rows = (
        db.query(MarketingPerformance)
        .filter(MarketingPerformance.user_id == user_id)
        .all()
    )

    # ---------------------------------------------------------
    # 1. Customer feedback summary
    # ---------------------------------------------------------

    sentiment_counts = {
        "Positive": 0,
        "Neutral": 0,
        "Negative": 0,
    }

    theme_counts: Counter[str] = Counter()

    for feedback in feedback_rows:
        sentiment = feedback.sentiment

        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

        # A theme should count at most once per review.
        if feedback.themes:
            for theme in set(feedback.themes):
                theme_counts[theme] += 1

    total_feedback = len(feedback_rows)

    if total_feedback:
        sentiment_percentages = {
            sentiment: round(
                count / total_feedback * 100,
                2,
            )
            for sentiment, count in sentiment_counts.items()
        }
    else:
        sentiment_percentages = {
            "Positive": 0.0,
            "Neutral": 0.0,
            "Negative": 0.0,
        }

    feedback_summary = {
        "total_feedback": total_feedback,
        "average_rating": _calculate_average_rating(
            feedback_rows
        ),
        "sentiment_counts": sentiment_counts,
        "sentiment_percentages": sentiment_percentages,
        "complaint_themes": [
            {
                "theme": theme,
                "count": count,
            }
            for theme, count in sorted(
                theme_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ],
    }

    # ---------------------------------------------------------
    # 2. Marketing performance summary
    # ---------------------------------------------------------

    metric_names = [
        "reach",
        "impressions",
        "clicks",
        "likes",
        "comments",
        "shares",
        "conversions",
    ]

    metric_totals = {
        metric: _aggregate_metric(
            marketing_rows,
            metric,
        )
        for metric in metric_names
    }

    rates = calculate_marketing_rates(
        reach=metric_totals["reach"],
        impressions=metric_totals["impressions"],
        clicks=metric_totals["clicks"],
        likes=metric_totals["likes"],
        comments=metric_totals["comments"],
        shares=metric_totals["shares"],
        conversions=metric_totals["conversions"],
    )

    marketing_summary = {
        "total_posts": len(marketing_rows),
        "metric_totals": metric_totals,
        "click_through_rate": rates["click_through_rate"],
        "engagement_rate": rates["engagement_rate"],
        "conversion_rate": rates["conversion_rate"],
    }

    # ---------------------------------------------------------
    # 3. Combined analytics response
    # ---------------------------------------------------------

    return {
        "feedback": feedback_summary,
        "marketing": marketing_summary,
    }