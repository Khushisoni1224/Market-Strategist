"""Validate and import marketing performance data from CSV files."""

import csv
import io
import re
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.marketing_import import MarketingImport
from app.models.marketing_performance import MarketingPerformance


MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_ROWS = 10_000

DATE_COLUMNS = {
    "content date",
    "content_date",
    "date",
    "post date",
    "post_date",
}

CONTENT_ID_COLUMNS = {
    "content id",
    "content_id",
    "post id",
    "post_id",
    "post",
}

OPTIONAL_TEXT_COLUMNS = {
    "platform": {"platform", "social platform", "social_platform"},
    "content_type": {"content type", "content_type", "post type", "post_type"},
}

METRIC_COLUMNS = {
    "reach": {"reach"},
    "impressions": {"impressions"},
    "clicks": {"clicks"},
    "likes": {"likes"},
    "comments": {"comments"},
    "shares": {"shares"},
    "conversions": {"conversions"},
}


class MarketingImportError(ValueError):
    """Raised when a marketing CSV file is invalid."""


def _normalize_header(header: str) -> str:
    """Normalize a CSV column name for consistent matching."""
    return re.sub(r"\s+", " ", header.strip().lower())


def _decode_csv(file_bytes: bytes) -> str:
    """Decode CSV content, supporting common Windows-exported files."""
    if not file_bytes:
        raise MarketingImportError("The uploaded CSV file is empty.")

    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise MarketingImportError(
        "The file encoding is not supported. Save it as UTF-8 CSV."
    )


def _parse_csv(
    file_bytes: bytes,
) -> tuple[list[str], list[dict[str, str]]]:
    """Validate the CSV structure and return normalized rows."""
    if len(file_bytes) > MAX_FILE_SIZE:
        raise MarketingImportError(
            "CSV file must not exceed 5 MB."
        )

    text = _decode_csv(file_bytes)

    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
        original_headers = reader.fieldnames

        if not original_headers:
            raise MarketingImportError(
                "The CSV must contain a header row."
            )

        headers = [
            _normalize_header(header or "")
            for header in original_headers
        ]

        if any(not header for header in headers):
            raise MarketingImportError(
                "CSV headers cannot be blank."
            )

        if len(headers) != len(set(headers)):
            raise MarketingImportError(
                "CSV contains duplicate column names."
            )

        if not any(header in DATE_COLUMNS for header in headers):
            raise MarketingImportError(
                "CSV must contain a date or content date column."
            )

        if not any(
            header in CONTENT_ID_COLUMNS for header in headers
        ):
            raise MarketingImportError(
                "CSV must contain a content ID or post ID column."
            )

        rows: list[dict[str, str]] = []

        for row_number, row in enumerate(reader, start=2):
            if row_number - 1 > MAX_ROWS:
                raise MarketingImportError(
                    "CSV cannot contain more than 10,000 data rows."
                )

            if None in row:
                raise MarketingImportError(
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
        raise MarketingImportError(
            f"Could not read the CSV file: {exc}"
        ) from exc


def _get_column_value(
    row: dict[str, str],
    accepted_names: set[str],
) -> str:
    """Read a value from the first matching column name."""
    for name in accepted_names:
        if name in row:
            return row[name]

    return ""


def _parse_date(value: str, row_number: int) -> date:
    """Parse a content date in ISO or common day/month formats."""
    if not value:
        raise MarketingImportError(
            f"Date is required in row {row_number}."
        )

    supported_formats = (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    )

    for date_format in supported_formats:
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue

    raise MarketingImportError(
        f"Date in row {row_number} is invalid. "
        "Use YYYY-MM-DD or another supported date format."
    )


def _parse_metric(
    value: str,
    metric_name: str,
    row_number: int,
) -> int | None:
    """Parse a non-negative whole-number metric; blanks remain NULL."""
    if not value:
        return None

    try:
        number = float(value)
    except ValueError as exc:
        raise MarketingImportError(
            f"{metric_name} in row {row_number} must be a "
            "non-negative whole number or blank."
        ) from exc

    if not number.is_integer() or number < 0:
        raise MarketingImportError(
            f"{metric_name} in row {row_number} must be a "
            "non-negative whole number or blank."
        )

    return int(number)


def _get_metric_values(
    row: dict[str, str],
    row_number: int,
) -> dict[str, int | None]:
    """Parse every supported marketing metric."""
    values: dict[str, int | None] = {}

    for metric_name, aliases in METRIC_COLUMNS.items():
        raw_value = _get_column_value(row, aliases)

        values[metric_name] = _parse_metric(
            raw_value,
            metric_name,
            row_number,
        )

    return values


def process_marketing_csv(
    db: Session,
    user_id: int,
    filename: str,
    file_bytes: bytes,
) -> dict[str, Any]:
    """
    Import marketing performance data for one user.

    Existing records are updated when user_id, content_date, and
    content_id match. Otherwise, a new record is created.

    Invalid data rows are counted and skipped. Invalid CSV structure
    raises MarketingImportError.
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("A valid user ID is required.")

    safe_filename = (
        (filename or "marketing.csv")
        .replace("\\", "/")
        .split("/")[-1]
    )
    safe_filename = safe_filename[:255] or "marketing.csv"

    headers, rows = _parse_csv(file_bytes)

    date_column = next(
        header for header in headers if header in DATE_COLUMNS
    )
    content_id_column = next(
        header for header in headers if header in CONTENT_ID_COLUMNS
    )

    import_record = MarketingImport(
        user_id=user_id,
        filename=safe_filename,
        status="processing",
        total_rows=len(rows),
        saved_rows=0,
        updated_rows=0,
        invalid_rows=0,
    )

    try:
        db.add(import_record)
        db.flush()

        saved_rows = 0
        updated_rows = 0
        invalid_rows = 0

        for row_number, row in enumerate(rows, start=2):
            try:
                content_date = _parse_date(
                    row.get(date_column, ""),
                    row_number,
                )

                content_id = row.get(
                    content_id_column, ""
                ).strip()

                if not content_id:
                    raise MarketingImportError(
                        f"Content ID is required in row {row_number}."
                    )

                metric_values = _get_metric_values(
                    row,
                    row_number,
                )

                platform = _get_column_value(
                    row,
                    OPTIONAL_TEXT_COLUMNS["platform"],
                )

                content_type = _get_column_value(
                    row,
                    OPTIONAL_TEXT_COLUMNS["content_type"],
                )

                existing_record = db.scalar(
                    select(MarketingPerformance).where(
                        MarketingPerformance.user_id == user_id,
                        MarketingPerformance.content_date == content_date,
                        MarketingPerformance.content_id == content_id,
                    )
                )

                if existing_record is not None:
                    # Update the existing record instead of duplicating it.
                    existing_record.marketing_import_id = import_record.id
                    existing_record.platform = platform or None
                    existing_record.content_type = content_type or None

                    for metric_name, metric_value in metric_values.items():
                        setattr(
                            existing_record,
                            metric_name,
                            metric_value,
                        )

                    updated_rows += 1

                else:
                    new_record = MarketingPerformance(
                        user_id=user_id,
                        marketing_import_id=import_record.id,
                        content_date=content_date,
                        content_id=content_id,
                        platform=platform or None,
                        content_type=content_type or None,
                        **metric_values,
                    )

                    db.add(new_record)
                    saved_rows += 1

                # Make the row visible to later rows in the same CSV.
                # This also ensures duplicate keys within one upload
                # update the record rather than creating duplicates.
                db.flush()

            except MarketingImportError:
                invalid_rows += 1

        import_record.status = "completed"
        import_record.saved_rows = saved_rows
        import_record.updated_rows = updated_rows
        import_record.invalid_rows = invalid_rows
        import_record.completed_at = datetime.now(timezone.utc)

        db.commit()

        return {
            "import_id": import_record.id,
            "filename": safe_filename,
            "status": import_record.status,
            "total_rows": import_record.total_rows,
            "saved_rows": saved_rows,
            "updated_rows": updated_rows,
            "invalid_rows": invalid_rows,
        }

    except Exception:
        db.rollback()
        raise