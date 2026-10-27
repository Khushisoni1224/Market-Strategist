"""Validate, analyze, and import customer feedback from CSV files."""

import csv
import io
import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer_feedback import CustomerFeedback
from app.models.feedback_import import FeedbackImport
from app.models.product import Product
from app.services.complaint_service import detect_complaint_themes
from app.services.pii import mask_personal_information
from app.services.sentiment_service import analyze_sentiment


MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_ROWS = 10_000

REQUIRED_REVIEW_COLUMNS = {
    "review text",
    "review_text",
    "review",
    "feedback",
}

RATING_COLUMNS = {"rating", "review rating", "review_rating"}

PRODUCT_COLUMNS = {"product", "product name", "product_name"}


class FeedbackImportError(ValueError):
    """Raised when an uploaded feedback CSV cannot be imported."""


def _normalize_header(header: str) -> str:
    """Normalize a CSV column name for flexible matching."""
    return re.sub(r"\s+", " ", header.strip().lower())


def _decode_csv(file_bytes: bytes) -> str:
    """Decode a CSV using common encodings."""
    if not file_bytes:
        raise FeedbackImportError("The uploaded CSV file is empty.")

    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise FeedbackImportError(
        "The file encoding is not supported. Save it as UTF-8 CSV."
    )


def _parse_csv(file_bytes: bytes) -> tuple[list[str], list[dict[str, str]]]:
    """Validate CSV headers and return its data rows."""
    if len(file_bytes) > MAX_FILE_SIZE:
        raise FeedbackImportError("CSV file must not exceed 5 MB.")

    text = _decode_csv(file_bytes)

    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
        original_headers = reader.fieldnames

        if not original_headers:
            raise FeedbackImportError("The CSV must contain a header row.")

        headers = [_normalize_header(h or "") for h in original_headers]

        if any(not header for header in headers):
            raise FeedbackImportError("CSV headers cannot be blank.")

        if len(headers) != len(set(headers)):
            raise FeedbackImportError(
                "CSV contains duplicate column names."
            )

        if not any(header in REQUIRED_REVIEW_COLUMNS for header in headers):
            raise FeedbackImportError(
                "CSV must contain a Review Text, review, or feedback column."
            )

        rows: list[dict[str, str]] = []

        for row_number, row in enumerate(reader, start=2):
            if row_number - 1 > MAX_ROWS:
                raise FeedbackImportError(
                    "CSV cannot contain more than 10,000 data rows."
                )

            # DictReader uses a None key for rows with extra columns.
            if None in row:
                raise FeedbackImportError(
                    f"Row {row_number} contains more values than the header."
                )

            normalized_row = {
                _normalize_header(key): (value or "").strip()
                for key, value in row.items()
                if key is not None
            }

            rows.append(normalized_row)

        return headers, rows

    except csv.Error as exc:
        raise FeedbackImportError(
            f"Could not read the CSV file: {exc}"
        ) from exc


def _get_column_value(
    row: dict[str, str],
    accepted_names: set[str],
) -> str:
    """Get a value from the first matching column name."""
    for name in accepted_names:
        if name in row:
            return row[name]
    return ""


def _parse_rating(value: str, row_number: int) -> int | None:
    """Parse an optional integer rating between 1 and 5."""
    if not value:
        return None

    try:
        rating_number = float(value)
    except ValueError as exc:
        raise FeedbackImportError(
            f"Rating in row {row_number} must be a number from 1 to 5."
        ) from exc

    if not rating_number.is_integer() or not 1 <= rating_number <= 5:
        raise FeedbackImportError(
            f"Rating in row {row_number} must be a whole number from 1 to 5."
        )

    return int(rating_number)


def process_feedback_csv(
    db: Session,
    user_id: int,
    filename: str,
    file_bytes: bytes,
) -> dict[str, Any]:
    """
    Import customer feedback for one user.

    The file is validated before database records are created.
    If processing fails, database changes are rolled back.
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("A valid user ID is required.")

    safe_filename = (filename or "feedback.csv").replace("\\", "/").split("/")[-1]
    safe_filename = safe_filename[:255] or "feedback.csv"

    headers, rows = _parse_csv(file_bytes)

    review_column = next(
        header for header in headers
        if header in REQUIRED_REVIEW_COLUMNS
    )

    rating_column = next(
        (header for header in headers if header in RATING_COLUMNS),
        None,
    )

    product_column = next(
        (header for header in headers if header in PRODUCT_COLUMNS),
        None,
    )

    # Build a product lookup restricted to the current user.
    products = db.scalars(
        select(Product).where(Product.user_id == user_id)
    ).all()

    product_lookup = {
        product.name.strip().casefold(): product.id
        for product in products
        if product.name and product.name.strip()
    }

    import_record = FeedbackImport(
        user_id=user_id,
        filename=safe_filename,
        status="processing",
        total_rows=len(rows),
        saved_rows=0,
        failed_rows=0,
    )

    try:
        db.add(import_record)
        db.flush()

        saved_rows = 0
        failed_rows = 0

        for row_number, row in enumerate(rows, start=2):
            review_text = row.get(review_column, "").strip()

            # Blank review rows are skipped and recorded as failed rows.
            if not review_text:
                failed_rows += 1
                continue

            try:
                rating = (
                    _parse_rating(row.get(rating_column, ""), row_number)
                    if rating_column
                    else None
                )

                masked_review = mask_personal_information(review_text)
                sentiment_result = analyze_sentiment(masked_review)

                themes = detect_complaint_themes(
                    masked_review,
                    str(sentiment_result["sentiment"]),
                )

                product_id = None
                if product_column:
                    product_name = row.get(product_column, "").strip()
                    product_id = product_lookup.get(product_name.casefold())

                feedback = CustomerFeedback(
                    user_id=user_id,
                    feedback_import_id=import_record.id,
                    review_text=masked_review,
                    rating=rating,
                    sentiment=str(sentiment_result["sentiment"]),
                    sentiment_score=float(
                        sentiment_result["sentiment_score"]
                    ),
                    themes=themes,
                    product_id=product_id,
                )

                db.add(feedback)
                saved_rows += 1

            except FeedbackImportError:
                # A malformed rating invalidates this individual row.
                failed_rows += 1

        import_record.status = "completed"
        import_record.saved_rows = saved_rows
        import_record.failed_rows = failed_rows
        import_record.completed_at = datetime.now(timezone.utc)

        db.commit()

        return {
            "import_id": import_record.id,
            "filename": safe_filename,
            "status": import_record.status,
            "total_rows": import_record.total_rows,
            "saved_rows": saved_rows,
            "failed_rows": failed_rows,
        }

    except Exception:
        db.rollback()
        raise