
import io
import re

import pandas as pd
from django.db import transaction

from .models import CustomerFeedback, FeedbackImport
from .sentiment import analyze_single_review


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_ROWS = 10000


def mask_personal_information(text):
    """Mask common email addresses and phone numbers."""

    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL MASKED]",
        text,
    )

    text = re.sub(
        r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)",
        "[PHONE MASKED]",
        text,
    )

    return text


def process_feedback_csv(uploaded_file):
    """Validate, analyze, and save uploaded customer feedback."""

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

        df = pd.read_csv(
            io.StringIO(decoded_data),
            dtype=str,
            keep_default_na=False,
            on_bad_lines="error",
        )

    except (pd.errors.ParserError, pd.errors.EmptyDataError):
        raise ValueError(
            "The CSV file could not be read. Check its rows and columns."
        )
    except (UnicodeDecodeError, LookupError):
        raise ValueError(
            "The CSV encoding is unsupported. Please save it as UTF-8."
        )
    except Exception as exc:
        raise ValueError(
            "Unable to read the uploaded CSV file."
        ) from exc

    if len(df.columns) == 0:
        raise ValueError("The CSV file must contain column headers.")

    df.columns = [str(column).strip() for column in df.columns]

    if len(set(df.columns)) != len(df.columns):
        raise ValueError("The CSV contains duplicate column names.")

    review_column = next(
        (
            column
            for column in df.columns
            if column.casefold() == "review text"
        ),
        None,
    )

    if review_column is None:
        raise ValueError(
            'Required column "Review Text" is missing.'
        )

    if len(df) > MAX_ROWS:
        raise ValueError(
            f"The CSV contains more than {MAX_ROWS} data rows."
        )

    total_rows = len(df)
    valid_reviews = []
    invalid_count = 0
    warnings = []

    # Analyze the reviews before saving anything.
    for row_number, review_text in enumerate(
        df[review_column].tolist(),
        start=2,
    ):
        review_text = str(review_text).strip()

        if not review_text:
            invalid_count += 1
            continue

        sanitized_text = mask_personal_information(review_text)
        sentiment_result = analyze_single_review(sanitized_text)

        valid_reviews.append({
            "row_number": row_number,
            "review_text": sanitized_text,
            "sentiment": sentiment_result["sentiment"],
            "score": sentiment_result["sentiment_score"],
        })

    if invalid_count:
        warnings.append(
            f"{invalid_count} row(s) have empty review text and were skipped."
        )

    if total_rows == 0:
        warnings.append("The CSV contains headers but no data rows.")

    if len(valid_reviews) < 5:
        warnings.append(
            "The dataset contains fewer than five valid reviews; "
            "aggregate conclusions may be unreliable."
        )

    # Save the import record and all its valid reviews together.
    import_record = None

    try:
        with transaction.atomic():
            import_record = FeedbackImport.objects.create(
                filename=filename,
                status="processing",
                total_rows=total_rows,
                valid_count=len(valid_reviews),
                invalid_count=invalid_count,
                analyzed_count=len(valid_reviews),
            )

            CustomerFeedback.objects.bulk_create([
                CustomerFeedback(
                    import_record=import_record,
                    row_number=review["row_number"],
                    review_text=review["review_text"],
                    sentiment=review["sentiment"],
                    sentiment_score=review["score"],
                )
                for review in valid_reviews
            ])

            import_record.status = "completed"
            import_record.save(update_fields=["status"])

    except Exception as exc:
        raise ValueError(
            "The reviews could not be saved to the database. "
            "Please try again."
        ) from exc

    return {
        "import_id": import_record.pk,
        "filename": filename,
        "status": import_record.status,
        "total_rows": total_rows,
        "valid_count": len(valid_reviews),
        "invalid_count": invalid_count,
        "analyzed_count": len(valid_reviews),
        "warnings": warnings,
        "preview": valid_reviews[:100],
    }
