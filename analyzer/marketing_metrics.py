
from django.db.models import Sum, Count
from .models import MarketingPerformance


def calculate_rate(numerator, denominator):
    """
    Calculate a percentage only when both values are available
    and the denominator is greater than zero.
    """
    if numerator is None or denominator is None:
        return None

    if denominator <= 0 or numerator < 0:
        return None

    return round((numerator / denominator) * 100, 2)


def calculate_marketing_summary(queryset=None):
    """
    Calculate overall marketing performance from database records.

    Missing metrics are excluded from totals. Their counts are
    also returned so the dashboard can show data completeness.
    """
    if queryset is None:
        queryset = MarketingPerformance.objects.all()

    aggregates = queryset.aggregate(
        record_count=Count("id"),
        total_reach=Sum("reach"),
        reach_count=Count("reach"),
        total_impressions=Sum("impressions"),
        impressions_count=Count("impressions"),
        total_views=Sum("views"),
        views_count=Count("views"),
        total_likes=Sum("likes"),
        likes_count=Count("likes"),
        total_comments=Sum("comments"),
        comments_count=Count("comments"),
        total_saves=Sum("saves"),
        saves_count=Count("saves"),
        total_shares=Sum("shares"),
        shares_count=Count("shares"),
        total_clicks=Sum("clicks"),
        clicks_count=Count("clicks"),
        total_enquiries=Sum("enquiries"),
        enquiries_count=Count("enquiries"),
        total_conversions=Sum("conversions"),
        conversions_count=Count("conversions"),
    )

    engagement_components = [
        aggregates["total_likes"],
        aggregates["total_comments"],
        aggregates["total_saves"],
        aggregates["total_shares"],
    ]

    engagement_counts = [
        aggregates["likes_count"],
        aggregates["comments_count"],
        aggregates["saves_count"],
        aggregates["shares_count"],
    ]

    # Engagement is reported only when all four components
    # are available for every record in the selected dataset.
    complete_engagement_data = (
        aggregates["record_count"] > 0
        and all(
            count == aggregates["record_count"]
            for count in engagement_counts
        )
    )

    if complete_engagement_data:
        total_engagement = sum(engagement_components)
    else:
        total_engagement = None

    impressions = aggregates["total_impressions"]
    clicks = aggregates["total_clicks"]
    conversions = aggregates["total_conversions"]

    # Only calculate a rate if its numerator and denominator
    # are present for every record in this dataset.
    complete_impressions = (
        aggregates["record_count"] > 0
        and aggregates["impressions_count"] == aggregates["record_count"]
    )

    complete_clicks = (
        aggregates["record_count"] > 0
        and aggregates["clicks_count"] == aggregates["record_count"]
    )

    complete_conversions = (
        aggregates["record_count"] > 0
        and aggregates["conversions_count"] == aggregates["record_count"]
    )

    engagement_rate = None
    if complete_engagement_data and complete_impressions:
        engagement_rate = calculate_rate(
            total_engagement, impressions
        )

    click_through_rate = None
    if complete_clicks and complete_impressions:
        click_through_rate = calculate_rate(
            clicks, impressions
        )

    conversion_rate = None
    if complete_conversions and complete_clicks:
        conversion_rate = calculate_rate(
            conversions, clicks
        )

    return {
        "record_count": aggregates["record_count"],
        "total_reach": aggregates["total_reach"],
        "reach_count": aggregates["reach_count"],
        "total_impressions": impressions,
        "impressions_count": aggregates["impressions_count"],
        "total_views": aggregates["total_views"],
        "views_count": aggregates["views_count"],
        "total_likes": aggregates["total_likes"],
        "total_comments": aggregates["total_comments"],
        "total_saves": aggregates["total_saves"],
        "total_shares": aggregates["total_shares"],
        "total_engagement": total_engagement,
        "total_clicks": clicks,
        "clicks_count": aggregates["clicks_count"],
        "total_enquiries": aggregates["total_enquiries"],
        "total_conversions": conversions,
        "conversions_count": aggregates["conversions_count"],
        "engagement_rate": engagement_rate,
        "click_through_rate": click_through_rate,
        "conversion_rate": conversion_rate,
        "complete_engagement_data": complete_engagement_data,
    }
