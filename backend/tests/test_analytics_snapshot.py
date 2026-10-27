"""Tests for the analytics snapshot service."""

from datetime import date, datetime

from app.models.customer_feedback import CustomerFeedback
from app.models.feedback_import import FeedbackImport
from app.models.marketing_import import MarketingImport
from app.models.marketing_performance import MarketingPerformance
from app.services.analytics_snapshot import get_analytics_snapshot


def create_feedback_import(db, user_id):
    """Create a feedback import record for test data."""
    record = FeedbackImport(
        user_id=user_id,
        filename="reviews.csv",
        status="completed",
        total_rows=3,
        saved_rows=3,
        failed_rows=0,
    )
    db.add(record)
    db.flush()
    return record


def create_marketing_import(db, user_id):
    """Create a marketing import record for test data."""
    record = MarketingImport(
        user_id=user_id,
        filename="marketing.csv",
        status="completed",
        total_rows=2,
        saved_rows=2,
        updated_rows=0,
        invalid_rows=0,
    )
    db.add(record)
    db.flush()
    return record


def test_analytics_feedback_summary(client, session_factory):
    """Feedback totals, ratings, sentiment and themes should be correct."""
    with session_factory() as db:
        user = db.query(
            __import__(
                "app.models.user",
                fromlist=["User"],
            ).User
        ).first()

        if user is None:
            from app.models.user import User

            user = User(
                email="analytics-test@example.com",
                hashed_password="test-password",
                is_active=True,
            )
            db.add(user)
            db.flush()

        feedback_import = create_feedback_import(
            db,
            user.id,
        )

        db.add_all(
            [
                CustomerFeedback(
                    user_id=user.id,
                    feedback_import_id=feedback_import.id,
                    review_text="Good product",
                    rating=5,
                    sentiment="Positive",
                    sentiment_score=0.8,
                    themes=[],
                ),
                CustomerFeedback(
                    user_id=user.id,
                    feedback_import_id=feedback_import.id,
                    review_text="Poor fit",
                    rating=2,
                    sentiment="Negative",
                    sentiment_score=-0.7,
                    themes=["Size and Fit", "Size and Fit"],
                ),
                CustomerFeedback(
                    user_id=user.id,
                    feedback_import_id=feedback_import.id,
                    review_text="Average product",
                    rating=3,
                    sentiment="Neutral",
                    sentiment_score=0.0,
                    themes=[],
                ),
            ]
        )
        db.commit()

        result = get_analytics_snapshot(db, user.id)

        feedback = result["feedback"]

        assert feedback["total_feedback"] == 3
        assert feedback["average_rating"] == 3.33

        assert feedback["sentiment_counts"] == {
            "Positive": 1,
            "Neutral": 1,
            "Negative": 1,
        }

        assert feedback["sentiment_percentages"] == {
            "Positive": 33.33,
            "Neutral": 33.33,
            "Negative": 33.33,
        }

        assert feedback["complaint_themes"] == [
            {"theme": "Size and Fit", "count": 1}
        ]


def test_analytics_marketing_summary(client, session_factory):
    """Marketing totals and rates should be calculated correctly."""
    with session_factory() as db:
        from app.models.user import User

        user = User(
            email="marketing-analytics-test@example.com",
            hashed_password="test-password",
            is_active=True,
        )
        db.add(user)
        db.flush()

        marketing_import = create_marketing_import(
            db,
            user.id,
        )

        db.add_all(
            [
                MarketingPerformance(
                    user_id=user.id,
                    marketing_import_id=marketing_import.id,
                    content_date=date(2026, 10, 20),
                    content_id="post-1",
                    platform="Instagram",
                    content_type="Post",
                    reach=1000,
                    impressions=1500,
                    clicks=100,
                    likes=80,
                    comments=10,
                    shares=5,
                    conversions=4,
                ),
                MarketingPerformance(
                    user_id=user.id,
                    marketing_import_id=marketing_import.id,
                    content_date=date(2026, 10, 21),
                    content_id="post-2",
                    platform="Instagram",
                    content_type="Post",
                    reach=1000,
                    impressions=1500,
                    clicks=200,
                    likes=100,
                    comments=20,
                    shares=10,
                    conversions=6,
                ),
            ]
        )
        db.commit()

        result = get_analytics_snapshot(db, user.id)

        marketing = result["marketing"]

        assert marketing["total_posts"] == 2

        assert marketing["metric_totals"] == {
            "reach": 2000,
            "impressions": 3000,
            "clicks": 300,
            "likes": 180,
            "comments": 30,
            "shares": 15,
            "conversions": 10,
        }

        assert marketing["click_through_rate"] == 10.0
        assert marketing["engagement_rate"] == 11.25
        assert marketing["conversion_rate"] == 3.33


def test_analytics_empty_data(client, session_factory):
    """Users without imported data should receive an empty summary."""
    with session_factory() as db:
        from app.models.user import User

        user = User(
            email="empty-analytics-test@example.com",
            hashed_password="test-password",
            is_active=True,
        )
        db.add(user)
        db.commit()

        result = get_analytics_snapshot(db, user.id)

        assert result["feedback"]["total_feedback"] == 0
        assert result["feedback"]["average_rating"] is None

        assert result["feedback"]["sentiment_counts"] == {
            "Positive": 0,
            "Neutral": 0,
            "Negative": 0,
        }

        assert result["feedback"]["complaint_themes"] == []

        assert result["marketing"]["total_posts"] == 0

        assert result["marketing"]["metric_totals"] == {
            "reach": None,
            "impressions": None,
            "clicks": None,
            "likes": None,
            "comments": None,
            "shares": None,
            "conversions": None,
        }

        assert result["marketing"]["click_through_rate"] is None
        assert result["marketing"]["engagement_rate"] is None
        assert result["marketing"]["conversion_rate"] is None


def test_analytics_isolates_users(client, session_factory):
    """Analytics must not include another user's records."""
    with session_factory() as db:
        from app.models.user import User

        owner = User(
            email="analytics-owner@example.com",
            hashed_password="test-password",
            is_active=True,
        )
        other_user = User(
            email="analytics-other@example.com",
            hashed_password="test-password",
            is_active=True,
        )

        db.add_all([owner, other_user])
        db.flush()

        feedback_import = create_feedback_import(
            db,
            owner.id,
        )

        db.add(
            CustomerFeedback(
                user_id=owner.id,
                feedback_import_id=feedback_import.id,
                review_text="Excellent product",
                rating=5,
                sentiment="Positive",
                sentiment_score=0.9,
                themes=[],
            )
        )

        other_import = create_feedback_import(
            db,
            other_user.id,
        )

        db.add(
            CustomerFeedback(
                user_id=other_user.id,
                feedback_import_id=other_import.id,
                review_text="Terrible product",
                rating=1,
                sentiment="Negative",
                sentiment_score=-0.9,
                themes=["Fabric and Quality"],
            )
        )

        db.commit()

        owner_result = get_analytics_snapshot(
            db,
            owner.id,
        )

        other_result = get_analytics_snapshot(
            db,
            other_user.id,
        )

        assert owner_result["feedback"]["total_feedback"] == 1
        assert owner_result["feedback"]["sentiment_counts"]["Positive"] == 1
        assert owner_result["feedback"]["sentiment_counts"]["Negative"] == 0

        assert other_result["feedback"]["total_feedback"] == 1
        assert other_result["feedback"]["sentiment_counts"]["Negative"] == 1
        assert other_result["feedback"]["sentiment_counts"]["Positive"] == 0