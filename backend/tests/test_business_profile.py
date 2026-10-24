from tests.conftest import PROFILE

URL = "/api/v1/business-profile"


def test_get_missing_profile_is_404(client, auth_headers):
    assert client.get(URL, headers=auth_headers).status_code == 404


def test_put_creates_then_updates_same_row(client, auth_headers):
    r = client.put(URL, json=PROFILE, headers=auth_headers)
    assert r.status_code == 200
    created = r.json()
    assert created["business_name"] == "Cozy Candles"
    assert created["industry"] == "Home decor"
    assert created["business_model"] == "product"
    assert created["sales_channels"] == ["marketplace", "social_commerce"]
    assert created["onboarding_completed"] is True
    assert "password" not in created and "hashed_password" not in created

    updated = {**PROFILE, "business_name": "Cozy Candles Co", "business_model": "both", "goals": None}
    r = client.put(URL, json=updated, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]  # same row, not a second profile
    assert r.json()["business_model"] == "both"
    assert r.json()["goals"] is None

    r = client.get(URL, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["business_name"] == "Cozy Candles Co"


def test_optional_fields_can_be_omitted(client, auth_headers):
    minimal = {k: PROFILE[k] for k in ("business_name", "industry", "description", "business_model", "sales_channels")}
    r = client.put(URL, json=minimal, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["target_audience"] is None and body["website_url"] is None
    assert body["location"] is None and body["goals"] is None
    assert body["onboarding_completed"] is True


def test_required_fields_enforced(client, auth_headers):
    for field in ("business_name", "industry", "description", "business_model", "sales_channels"):
        body = {k: v for k, v in PROFILE.items() if k != field}
        assert client.put(URL, json=body, headers=auth_headers).status_code == 422, field


def test_validation_rules(client, auth_headers):
    bad_values = [
        {"business_name": "   "},
        {"description": "too short"},
        {"business_model": "hybrid"},
        {"sales_channels": []},
        {"sales_channels": ["carrier_pigeon"]},
        {"website_url": "not a url"},
        {"website_url": "javascript:alert(1)"},
        {"website_url": "ftp://files.example.com"},
        {"business_name": "x" * 201},
    ]
    for bad in bad_values:
        r = client.put(URL, json={**PROFILE, **bad}, headers=auth_headers)
        assert r.status_code == 422, bad
    assert client.get(URL, headers=auth_headers).status_code == 404  # nothing was saved


def test_normalization(client, auth_headers):
    body = {
        **PROFILE,
        "business_name": "  Cozy Candles  ",
        "sales_channels": ["marketplace", "marketplace", "own_website"],
        "target_audience": "   ",
        "location": "",
        "website_url": "  https://instagram.com/cozycandles  ",
    }
    r = client.put(URL, json=body, headers=auth_headers)
    assert r.status_code == 200
    out = r.json()
    assert out["business_name"] == "Cozy Candles"
    assert out["sales_channels"] == ["marketplace", "own_website"]
    assert out["target_audience"] is None and out["location"] is None
    assert out["website_url"].startswith("https://instagram.com/cozycandles")


def test_client_supplied_user_id_is_ignored(client, auth_headers):
    me = client.get("/api/v1/auth/me", headers=auth_headers).json()
    r = client.put(URL, json={**PROFILE, "user_id": 9999, "id": 77}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["user_id"] == me["id"]


def test_profiles_are_isolated_per_user(client, auth_headers, other_headers):
    client.put(URL, json=PROFILE, headers=auth_headers)
    assert client.get(URL, headers=other_headers).status_code == 404

    # Bob saving his profile must not touch Alice's.
    client.put(URL, json={**PROFILE, "business_name": "Bob's Bikes"}, headers=other_headers)
    assert client.get(URL, headers=auth_headers).json()["business_name"] == "Cozy Candles"
    assert client.get(URL, headers=other_headers).json()["business_name"] == "Bob's Bikes"
    a, b = client.get(URL, headers=auth_headers).json(), client.get(URL, headers=other_headers).json()
    assert a["id"] != b["id"] and a["user_id"] != b["user_id"]
