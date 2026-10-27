"""API tests for marketing performance endpoints."""

import csv
import io

import pytest


def make_csv(rows):
    """Create marketing CSV bytes for API tests."""
    output = io.StringIO()

    fieldnames = [
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
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    return output.getvalue().encode("utf-8")


def upload_csv(client, headers, rows, filename="marketing.csv"):
    """Upload a CSV using the authenticated API."""
    return client.post(
        "/api/v1/marketing/import",
        headers=headers,
        files={
            "file": (
                filename,
                make_csv(rows),
                "text/csv",
            )
        },
    )


def sample_row(
    content_id="post-001",
    content_date="2026-10-20",
    platform="Instagram",
):
    """Return one valid marketing data row."""
    return {
        "content_date": content_date,
        "content_id": content_id,
        "platform": platform,
        "content_type": "Post",
        "reach": "1000",
        "impressions": "1500",
        "clicks": "100",
        "likes": "80",
        "comments": "10",
        "shares": "5",
        "conversions": "4",
    }


def test_marketing_import_and_list(client, auth_headers):
    """Importing a CSV should expose saved records and calculated rates."""
    response = upload_csv(
        client,
        auth_headers,
        [
            sample_row(),
            sample_row(
                content_id="post-002",
                content_date="2026-10-21",
                platform="Facebook",
            ),
        ],
    )

    assert response.status_code == 201

    result = response.json()

    assert result["status"] == "completed"
    assert result["total_rows"] == 2
    assert result["saved_rows"] == 2
    assert result["updated_rows"] == 0
    assert result["invalid_rows"] == 0

    list_response = client.get(
        "/api/v1/marketing",
        headers=auth_headers,
    )

    assert list_response.status_code == 200

    data = list_response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 2

    newest_record = data["items"][0]

    assert newest_record["content_id"] == "post-002"
    assert newest_record["platform"] == "Facebook"
    assert newest_record["click_through_rate"] == 6.67
    assert newest_record["engagement_rate"] == 9.5
    assert newest_record["conversion_rate"] == 4.0


def test_marketing_platform_date_filters_and_pagination(
    client,
    auth_headers,
):
    """Platform/date filters and pagination should work together."""
    response = upload_csv(
        client,
        auth_headers,
        [
            sample_row("instagram-1", "2026-10-18", "Instagram"),
            sample_row("facebook-1", "2026-10-19", "Facebook"),
            sample_row("instagram-2", "2026-10-20", "Instagram"),
        ],
    )

    assert response.status_code == 201

    filtered_response = client.get(
        "/api/v1/marketing",
        headers=auth_headers,
        params={
            "platform": "instagram",
            "start_date": "2026-10-18",
            "end_date": "2026-10-20",
        },
    )

    assert filtered_response.status_code == 200

    filtered_data = filtered_response.json()

    assert filtered_data["total"] == 2
    assert all(
        item["platform"] == "Instagram"
        for item in filtered_data["items"]
    )

    paginated_response = client.get(
        "/api/v1/marketing",
        headers=auth_headers,
        params={"skip": 0, "limit": 1},
    )

    assert paginated_response.status_code == 200

    paginated_data = paginated_response.json()

    assert paginated_data["total"] == 3
    assert paginated_data["skip"] == 0
    assert paginated_data["limit"] == 1
    assert len(paginated_data["items"]) == 1


def test_marketing_import_updates_existing_record(
    client,
    auth_headers,
):
    """Repeated content/date imports should update the existing record."""
    first_response = upload_csv(
        client,
        auth_headers,
        [sample_row("repeat-post")],
    )

    assert first_response.status_code == 201
    assert first_response.json()["saved_rows"] == 1

    updated_row = sample_row("repeat-post")
    updated_row["reach"] = "2000"
    updated_row["impressions"] = "2500"

    second_response = upload_csv(
        client,
        auth_headers,
        [updated_row],
        filename="updated.csv",
    )

    assert second_response.status_code == 201
    assert second_response.json()["saved_rows"] == 0
    assert second_response.json()["updated_rows"] == 1

    list_response = client.get(
        "/api/v1/marketing",
        headers=auth_headers,
    )

    assert list_response.status_code == 200

    data = list_response.json()

    assert data["total"] == 1
    assert data["items"][0]["reach"] == 2000
    assert data["items"][0]["impressions"] == 2500


def test_marketing_records_and_history_are_user_scoped(
    client,
    auth_headers,
    other_headers,
):
    """A second user must not see the first user's records or history."""
    upload_response = upload_csv(
        client,
        auth_headers,
        [sample_row("private-post")],
    )

    assert upload_response.status_code == 201

    owner_records = client.get(
        "/api/v1/marketing",
        headers=auth_headers,
    )

    other_records = client.get(
        "/api/v1/marketing",
        headers=other_headers,
    )

    assert owner_records.status_code == 200
    assert owner_records.json()["total"] == 1

    assert other_records.status_code == 200
    assert other_records.json()["total"] == 0
    assert other_records.json()["items"] == []

    owner_history = client.get(
        "/api/v1/marketing/imports",
        headers=auth_headers,
    )

    other_history = client.get(
        "/api/v1/marketing/imports",
        headers=other_headers,
    )

    assert owner_history.status_code == 200
    assert owner_history.json()["total"] == 1

    assert other_history.status_code == 200
    assert other_history.json()["total"] == 0
    assert other_history.json()["items"] == []


def test_marketing_import_history_pagination(client, auth_headers):
    """Import history should support pagination."""
    for index in range(3):
        response = upload_csv(
            client,
            auth_headers,
            [
                sample_row(
                    content_id=f"history-post-{index}",
                    content_date=f"2026-10-{20 + index}",
                )
            ],
        )

        assert response.status_code == 201

    response = client.get(
        "/api/v1/marketing/imports",
        headers=auth_headers,
        params={"skip": 1, "limit": 1},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["skip"] == 1
    assert data["limit"] == 1
    assert len(data["items"]) == 1


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/api/v1/marketing"),
        ("get", "/api/v1/marketing/imports"),
    ],
)
def test_marketing_get_endpoints_require_authentication(
    client,
    method,
    path,
):
    """Marketing GET endpoints must require authentication."""
    response = getattr(client, method)(path)

    assert response.status_code in (401, 403)


def test_marketing_import_requires_authentication(client):
    """Uploading marketing data must require authentication."""
    response = client.post(
        "/api/v1/marketing/import",
        files={
            "file": (
                "marketing.csv",
                make_csv([sample_row()]),
                "text/csv",
            )
        },
    )

    assert response.status_code in (401, 403)


def test_marketing_import_rejects_non_csv_filename(
    client,
    auth_headers,
):
    """Non-CSV uploads should be rejected."""
    response = client.post(
        "/api/v1/marketing/import",
        headers=auth_headers,
        files={
            "file": (
                "marketing.txt",
                b"not a CSV file",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_marketing_import_rejects_missing_required_columns(
    client,
    auth_headers,
):
    """A CSV missing date and content ID columns should be rejected."""
    response = client.post(
        "/api/v1/marketing/import",
        headers=auth_headers,
        files={
            "file": (
                "invalid.csv",
                b"platform,reach,clicks\nInstagram,100,10\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400


def test_marketing_rejects_invalid_date_range(client, auth_headers):
    """The start date cannot be later than the end date."""
    response = client.get(
        "/api/v1/marketing",
        headers=auth_headers,
        params={
            "start_date": "2026-10-25",
            "end_date": "2026-10-20",
        },
    )

    assert response.status_code == 400