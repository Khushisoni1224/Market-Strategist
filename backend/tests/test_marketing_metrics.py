"""Tests for marketing performance rate calculations."""

from app.services.marketing_metrics import calculate_marketing_rates


def test_calculates_all_marketing_rates():
    result = calculate_marketing_rates(
        reach=1000,
        impressions=1500,
        clicks=100,
        likes=80,
        comments=10,
        shares=5,
        conversions=4,
    )

    assert result["click_through_rate"] == 6.67
    assert result["engagement_rate"] == 9.5
    assert result["conversion_rate"] == 4.0


def test_missing_metrics_return_none():
    result = calculate_marketing_rates(
        reach=1000,
        impressions=None,
        clicks=100,
        likes=80,
        comments=None,
        shares=5,
        conversions=None,
    )

    assert result["click_through_rate"] is None
    assert result["engagement_rate"] is None
    assert result["conversion_rate"] is None


def test_zero_denominators_return_none():
    result = calculate_marketing_rates(
        reach=0,
        impressions=0,
        clicks=0,
        likes=10,
        comments=5,
        shares=2,
        conversions=1,
    )

    assert result["click_through_rate"] is None
    assert result["engagement_rate"] is None
    assert result["conversion_rate"] is None


def test_zero_numerator_is_a_valid_zero_rate():
    result = calculate_marketing_rates(
        reach=100,
        impressions=200,
        clicks=0,
        likes=0,
        comments=0,
        shares=0,
        conversions=0,
    )

    assert result["click_through_rate"] == 0.0
    assert result["engagement_rate"] == 0.0
    assert result["conversion_rate"] is None


def test_engagement_rate_requires_all_engagement_metrics():
    result = calculate_marketing_rates(
        reach=100,
        impressions=200,
        clicks=20,
        likes=10,
        comments=None,
        shares=5,
        conversions=2,
    )

    assert result["click_through_rate"] == 10.0
    assert result["engagement_rate"] is None
    assert result["conversion_rate"] == 10.0