"""API tests for the analytics summary endpoint."""


def test_analytics_summary_requires_authentication(client):
    """The analytics endpoint should require authentication."""
    response = client.get("/api/v1/analytics/summary")

    assert response.status_code in (401, 403)


def test_analytics_summary_returns_expected_structure(
    client,
    auth_headers,
):
    """An authenticated user should receive both summaries."""
    response = client.get(
        "/api/v1/analytics/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "feedback" in data
    assert "marketing" in data

    feedback = data["feedback"]

    assert feedback["total_feedback"] == 0
    assert feedback["average_rating"] is None
    assert feedback["sentiment_counts"] == {
        "Positive": 0,
        "Neutral": 0,
        "Negative": 0,
    }
    assert feedback["sentiment_percentages"] == {
        "Positive": 0.0,
        "Neutral": 0.0,
        "Negative": 0.0,
    }
    assert feedback["complaint_themes"] == []

    marketing = data["marketing"]

    assert marketing["total_posts"] == 0
    assert marketing["metric_totals"] == {
        "reach": None,
        "impressions": None,
        "clicks": None,
        "likes": None,
        "comments": None,
        "shares": None,
        "conversions": None,
    }
    assert marketing["click_through_rate"] is None
    assert marketing["engagement_rate"] is None
    assert marketing["conversion_rate"] is None


def test_analytics_summary_is_user_scoped(
    client,
    auth_headers,
    other_headers,
):
    """A user's analytics must not include another user's records."""
    # Import feedback and marketing data for the first user.
    feedback_response = client.post(
        "/api/v1/feedback/import",
        headers=auth_headers,
        files={
            "file": (
                "reviews.csv",
                (
                    "Review Text,Rating\n"
                    "Excellent product,5\n"
                    "Terrible quality,1\n"
                ).encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert feedback_response.status_code == 201

    marketing_csv = (
        "content_date,content_id,platform,content_type,"
        "reach,impressions,clicks,likes,comments,shares,conversions\n"
        "2026-10-20,post-001,Instagram,Post,1000,1500,100,80,10,5,4\n"
    )

    marketing_response = client.post(
        "/api/v1/marketing/import",
        headers=auth_headers,
        files={
            "file": (
                "marketing.csv",
                marketing_csv.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert marketing_response.status_code == 201

    # The owner should see the imported data.
    owner_response = client.get(
        "/api/v1/analytics/summary",
        headers=auth_headers,
    )

    assert owner_response.status_code == 200

    owner_data = owner_response.json()

    assert owner_data["feedback"]["total_feedback"] == 2
    assert owner_data["marketing"]["total_posts"] == 1

    # A second user should see only their own empty summary.
    other_response = client.get(
        "/api/v1/analytics/summary",
        headers=other_headers,
    )

    assert other_response.status_code == 200

    other_data = other_response.json()

    assert other_data["feedback"]["total_feedback"] == 0
    assert other_data["marketing"]["total_posts"] == 0
    assert other_data["feedback"]["complaint_themes"] == []