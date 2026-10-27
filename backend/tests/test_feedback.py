"""Automated tests for the customer feedback API."""

import csv
import io


def make_csv(rows, headers=None):
    """Build CSV content for upload tests."""
    if headers is None:
        headers = ["review_text", "rating", "product_name"]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()


def upload_csv(client, headers, csv_content, filename="reviews.csv"):
    """Upload a CSV file through the feedback API."""
    return client.post(
        "/api/v1/feedback/import",
        headers=headers,
        files={
            "file": (
                filename,
                csv_content.encode("utf-8"),
                "text/csv",
            )
        },
    )


def create_product(client, headers, name="Lavender Candle"):
    """Create a product for product-matching tests."""
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "name": name,
            "category": "Candles",
            "price": 12.5,
            "inventory_count": 10,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_feedback_csv_import_masks_pii_and_analyzes_sentiment(
    client, auth_headers
):
    product = create_product(client, auth_headers)

    csv_content = make_csv(
        [
            [
                "The fabric is terrible and the quality is very poor. "
                "Contact customer@example.com or call 9876543210.",
                1,
                "Lavender Candle",
            ],
            [
                "I absolutely love this product! The quality is excellent.",
                5,
                "Lavender Candle",
            ],
            ["", 3, "Lavender Candle"],
        ]
    )

    response = upload_csv(client, auth_headers, csv_content)

    assert response.status_code == 201, response.text

    result = response.json()

    assert result["status"] == "completed"
    assert result["total_rows"] == 3
    assert result["saved_rows"] == 2
    assert result["failed_rows"] == 1

    feedback_response = client.get(
        "/api/v1/feedback",
        headers=auth_headers,
    )

    assert feedback_response.status_code == 200
    feedback_data = feedback_response.json()

    assert feedback_data["total"] == 2
    assert len(feedback_data["items"]) == 2

    negative_review = next(
        item
        for item in feedback_data["items"]
        if item["sentiment"] == "Negative"
    )

    assert "[EMAIL]" in negative_review["review_text"]
    assert "[PHONE]" in negative_review["review_text"]
    assert "customer@example.com" not in negative_review["review_text"]
    assert "9876543210" not in negative_review["review_text"]
    assert negative_review["rating"] == 1
    assert "Fabric and Quality" in negative_review["themes"]
    assert negative_review["product_id"] == product["id"]

    positive_review = next(
        item
        for item in feedback_data["items"]
        if item["sentiment"] == "Positive"
    )

    assert positive_review["rating"] == 5
    assert positive_review["product_id"] == product["id"]


def test_feedback_sentiment_filter_and_pagination(client, auth_headers):
    csv_content = make_csv(
        [
            ["I love this product. It is wonderful!", 5, ""],
            ["This product is terrible and very disappointing.", 1, ""],
            ["The package arrived today.", 3, ""],
        ]
    )

    response = upload_csv(client, auth_headers, csv_content)
    assert response.status_code == 201, response.text

    response = client.get(
        "/api/v1/feedback?sentiment=Negative",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["sentiment"] == "Negative"

    response = client.get(
        "/api/v1/feedback?skip=0&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 3
    assert data["skip"] == 0
    assert data["limit"] == 2
    assert len(data["items"]) == 2


def test_feedback_import_history_is_user_scoped(
    client, auth_headers, other_headers
):
    csv_content = make_csv(
        [["I love this product!", 5, ""]]
    )

    response = upload_csv(client, auth_headers, csv_content)
    assert response.status_code == 201, response.text

    owner_history = client.get(
        "/api/v1/feedback/imports",
        headers=auth_headers,
    )

    assert owner_history.status_code == 200
    assert owner_history.json()["total"] == 1

    other_history = client.get(
        "/api/v1/feedback/imports",
        headers=other_headers,
    )

    assert other_history.status_code == 200
    assert other_history.json()["total"] == 0

    other_feedback = client.get(
        "/api/v1/feedback",
        headers=other_headers,
    )

    assert other_feedback.status_code == 200
    assert other_feedback.json()["total"] == 0


def test_feedback_endpoints_require_authentication(client):
    response = client.get("/api/v1/feedback")
    assert response.status_code == 401

    response = client.get("/api/v1/feedback/imports")
    assert response.status_code == 401

    response = client.post(
        "/api/v1/feedback/import",
        files={
            "file": (
                "reviews.csv",
                b"review_text,rating\nI love this product,5\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 401


def test_feedback_upload_rejects_non_csv_filename(client, auth_headers):
    response = upload_csv(
        client,
        auth_headers,
        "review_text,rating\nI love this product,5\n",
        filename="reviews.txt",
    )

    assert response.status_code == 400
    assert "CSV" in response.json()["detail"]


def test_feedback_upload_rejects_missing_review_column(
    client, auth_headers
):
    csv_content = make_csv(
        [["5", "Lavender Candle"]],
        headers=["rating", "product_name"],
    )

    response = upload_csv(client, auth_headers, csv_content)

    assert response.status_code == 400
    assert "Review Text" in response.json()["detail"]