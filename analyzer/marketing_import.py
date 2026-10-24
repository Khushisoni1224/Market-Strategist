
import csv
import io
from datetime import date
from django.db import transaction
from .models import MarketingPerformance


MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_ROWS = 10000

REQUIRED_COLUMNS = [
    "content_date",
    "content_id",
    "content_type",
    "product_name",
]

METRIC_COLUMNS = [
    "reach",
    "impressions",
    "views",
    "likes",
    "comments",
    "saves",
    "shares",
    "profile_visits",
    "clicks",
    "enquiries",
    "conversions",
]


def process_marketing_csv(uploaded_file):
    if not uploaded_file:
        raise ValueError("Please select a CSV file.")

    filename = uploaded_file.name

    if not filename.lower().endswith(".csv"):
        raise ValueError("Only CSV files are supported.")

    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValueError("The maximum allowed file size is 5 MB.")

    if uploaded_file.size == 0:
        raise ValueError("The uploaded file is empty.")

    try:
        raw_data = uploaded_file.read()

        


        try:
          decoded_data = raw_data.decode("utf-8-sig")
        except UnicodeDecodeError:
          decoded_data = raw_data.decode("cp1252")

        
        
        reader = csv.DictReader(io.StringIO(decoded_data.lstrip("\ufeff")))

        if not reader.fieldnames or not any(
            header and header.strip() for header in reader.fieldnames
        ):
           raise ValueError(
           "The CSV must contain column headers. "
           "Open the file in Notepad and check its first line."
           )

        headers = [
            header.strip() if header else ""
            for header in reader.fieldnames
        ]

        if len(headers) != len(set(headers)):
            raise ValueError("The CSV contains duplicate column names.")

        reader.fieldnames = headers

        missing_columns = [
            column for column in REQUIRED_COLUMNS
            if column not in headers
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

        rows = list(reader)

    except ValueError:
        raise
    except (csv.Error, UnicodeDecodeError):
        raise ValueError(
            "The CSV could not be read. Check its format and encoding."
        )
    except Exception as exc:
        raise ValueError("Unable to read the uploaded CSV file.") from exc

    if len(rows) > MAX_ROWS:
        raise ValueError(
            f"The CSV contains more than {MAX_ROWS} data rows."
        )

    valid_records = []
    invalid_rows = []
    warnings = []

    for row_number, row in enumerate(rows, start=2):
        # Reject rows with extra or missing CSV fields.
        if None in row or any(value is None for value in row.values()):
            invalid_rows.append(
                f"Row {row_number}: inconsistent number of CSV fields."
            )
            continue

        row = {
            str(key).strip(): (
                value.strip() if isinstance(value, str) else value
            )
            for key, value in row.items()
        }

        missing_required = [
            column for column in REQUIRED_COLUMNS
            if not row.get(column)
        ]

        if missing_required:
            invalid_rows.append(
                f"Row {row_number}: missing "
                + ", ".join(missing_required)
                + "."
            )
            continue

        try:
            content_date = date.fromisoformat(row["content_date"])
        except ValueError:
            invalid_rows.append(
                f"Row {row_number}: content_date must use YYYY-MM-DD format."
            )
            continue

        record_data = {
            "content_date": content_date,
            "content_id": row["content_id"],
            "content_type": row["content_type"],
            "product_name": row["product_name"],
        }

        row_invalid = False

        for column in METRIC_COLUMNS:
            value = row.get(column, "")

            # Blank metrics remain NULL, not zero.
            if value == "":
                record_data[column] = None
                continue

            try:
                number = int(value)
                if number < 0:
                    raise ValueError
                record_data[column] = number
            except (ValueError, TypeError):
                invalid_rows.append(
                    f"Row {row_number}: {column} must be a "
                    "non-negative whole number or blank."
                )
                row_invalid = True
                break

        if not row_invalid:
            valid_records.append(record_data)

    if invalid_rows:
        warnings.append(
            f"{len(invalid_rows)} row(s) were rejected due to validation errors."
        )

    if not rows:
        warnings.append("The CSV contains headers but no data rows.")

    if len(valid_records) < 5:
        warnings.append(
            "Fewer than five valid records were found; "
            "performance comparisons may be unreliable."
        )

    saved_count = 0

    if valid_records:
        try:
            with transaction.atomic():
                MarketingPerformance.objects.bulk_create([
                    MarketingPerformance(**record)
                    for record in valid_records
                ])
            saved_count = len(valid_records)
        except Exception as exc:
            raise ValueError(
                "The marketing records could not be saved. Please try again."
            ) from exc

    return {
        "filename": filename,
        "total_rows": len(rows),
        "saved_count": saved_count,
        "invalid_count": len(invalid_rows),
        "warnings": warnings,
        "errors": invalid_rows[:50],
        "preview": valid_records[:10],
    }
