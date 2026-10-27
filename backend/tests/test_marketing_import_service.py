"""Tests for the marketing performance CSV import service."""

import csv
import io

from sqlalchemy import select

from app.models.marketing_import import MarketingImport
from app.models.marketing_performance import MarketingPerformance
from app.models.user import User
from app.services.marketing_import import (
    MarketingImportError,
    process_marketing_csv,
)


def make_csv(rows):
    """Create CSV bytes for testing."""
    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=[
            "content_date",
            "content_id",
            "platform",
            "content_type",
            "reach",
            "impressions",
            "clicks",
            "likes",
            "comments",
            "shares",
            "conversions",
        ],
    )

    writer.writeheader()
    writer.writerows(rows)

    return output.getvalue().encode("utf-8")


def create_user(db, email):
    """Create a user for the test."""
    user = User(
        email=email,
        hashed_password="test-password-hash",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def test_marketing_import_saves_new_records(client, session_factory):
    """A valid CSV should create marketing records and import history."""

    with session_factory() as db:
        user = create_user(db, "marketing-test@example.com")

        file_bytes = make_csv(
            [
                {
                    "content_date": "2026-10-20",
                    "content_id": "post-001",
                    "platform": "Instagram",
                    "content_type": "Reel",
                    "reach": "1000",
                    "impressions": "1500",
                    "clicks": "100",
                    "likes": "80",
                    "comments": "10",
                    "shares": "5",
                    "conversions": "4",
                }
            ]
        )

        result = process_marketing_csv(
            db=db,
            user_id=user.id,
            filename="marketing.csv",
            file_bytes=file_bytes,
        )

        assert result["status"] == "completed"
        assert result["total_rows"] == 1
        assert result["saved_rows"] == 1
        assert result["updated_rows"] == 0
        assert result["invalid_rows"] == 0

        record = db.scalar(
            select(MarketingPerformance).where(
                MarketingPerformance.user_id == user.id,
                MarketingPerformance.content_id == "post-001",
            )
        )

        assert record is not None
        assert record.reach == 1000
        assert record.impressions == 1500
        assert record.platform == "Instagram"

        history = db.scalar(
            select(MarketingImport).where(
                MarketingImport.id == result["import_id"]
            )
        )

        assert history is not None
        assert history.saved_rows == 1


def test_marketing_import_updates_duplicate_records(
    client,
    session_factory,
):
    """Importing the same content and date should update, not duplicate."""

    with session_factory() as db:
        user = create_user(db, "marketing-update@example.com")

        first_upload = make_csv(
            [
                {
                    "content_date": "2026-10-20",
                    "content_id": "post-002",
                    "platform": "Instagram",
                    "content_type": "Post",
                    "reach": "500",
                    "impressions": "700",
                    "clicks": "20",
                    "likes": "15",
                    "comments": "2",
                    "shares": "1",
                    "conversions": "1",
                }
            ]
        )

        first_result = process_marketing_csv(
            db=db,
            user_id=user.id,
            filename="first.csv",
            file_bytes=first_upload,
        )

        assert first_result["saved_rows"] == 1
        assert first_result["updated_rows"] == 0

        second_upload = make_csv(
            [
                {
                    "content_date": "2026-10-20",
                    "content_id": "post-002",
                    "platform": "Instagram",
                    "content_type": "Post",
                    "reach": "900",
                    "impressions": "1200",
                    "clicks": "45",
                    "likes": "30",
                    "comments": "6",
                    "shares": "3",
                    "conversions": "5",
                }
            ]
        )

        second_result = process_marketing_csv(
            db=db,
            user_id=user.id,
            filename="second.csv",
            file_bytes=second_upload,
        )

        assert second_result["saved_rows"] == 0
        assert second_result["updated_rows"] == 1

        records = db.scalars(
            select(MarketingPerformance).where(
                MarketingPerformance.user_id == user.id,
                MarketingPerformance.content_id == "post-002",
            )
        ).all()

        assert len(records) == 1
        assert records[0].reach == 900
        assert records[0].impressions == 1200
        assert records[0].conversions == 5


def test_marketing_import_keeps_blank_metrics_as_null(
    client,
    session_factory,
):
    """Missing metric values should remain NULL, not become zero."""

    with session_factory() as db:
        user = create_user(db, "marketing-null@example.com")

        file_bytes = make_csv(
            [
                {
                    "content_date": "2026-10-21",
                    "content_id": "post-003",
                    "platform": "Instagram",
                    "content_type": "Story",
                    "reach": "250",
                    "impressions": "",
                    "clicks": "",
                    "likes": "12",
                    "comments": "",
                    "shares": "",
                    "conversions": "",
                }
            ]
        )

        result = process_marketing_csv(
            db=db,
            user_id=user.id,
            filename="missing-metrics.csv",
            file_bytes=file_bytes,
        )

        assert result["saved_rows"] == 1
        assert result["invalid_rows"] == 0

        record = db.scalar(
            select(MarketingPerformance).where(
                MarketingPerformance.user_id == user.id,
                MarketingPerformance.content_id == "post-003",
            )
        )

        assert record is not None
        assert record.reach == 250
        assert record.impressions is None
        assert record.clicks is None
        assert record.likes == 12
        assert record.comments is None


def test_marketing_import_skips_invalid_metric_rows(
    client,
    session_factory,
):
    """Negative or non-numeric metrics should invalidate their row."""

    with session_factory() as db:
        user = create_user(db, "marketing-invalid@example.com")

        file_bytes = make_csv(
            [
                {
                    "content_date": "2026-10-21",
                    "content_id": "post-valid",
                    "platform": "Instagram",
                    "content_type": "Post",
                    "reach": "250",
                    "impressions": "300",
                    "clicks": "10",
                    "likes": "12",
                    "comments": "2",
                    "shares": "1",
                    "conversions": "1",
                },
                {
                    "content_date": "2026-10-21",
                    "content_id": "post-invalid",
                    "platform": "Instagram",
                    "content_type": "Post",
                    "reach": "-10",
                    "impressions": "300",
                    "clicks": "ten",
                    "likes": "12",
                    "comments": "2",
                    "shares": "1",
                    "conversions": "1",
                },
            ]
        )

        result = process_marketing_csv(
            db=db,
            user_id=user.id,
            filename="mixed-rows.csv",
            file_bytes=file_bytes,
        )

        assert result["total_rows"] == 2
        assert result["saved_rows"] == 1
        assert result["updated_rows"] == 0
        assert result["invalid_rows"] == 1

        records = db.scalars(
            select(MarketingPerformance).where(
                MarketingPerformance.user_id == user.id
            )
        ).all()

        assert len(records) == 1
        assert records[0].content_id == "post-valid"


def test_marketing_import_requires_date_and_content_id():
    """A CSV without the required columns should be rejected."""

    invalid_csv = (
        "platform,reach,clicks\n"
        "Instagram,100,10\n"
    ).encode("utf-8")

    try:
        from app.services.marketing_import import _parse_csv

        _parse_csv(invalid_csv)

        assert False, "Expected MarketingImportError"

    except MarketingImportError as exc:
        assert "date" in str(exc).lower()