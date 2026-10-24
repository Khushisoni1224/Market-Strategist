from app.models.business_profile import BusinessProfile
from app.services.business_context import build_business_context, get_business_context_for_user
from tests.conftest import PROFILE


def test_new_user_must_start_onboarding(client, auth_headers):
    r = client.get("/api/v1/onboarding/status", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == {
        "profile_exists": False,
        "onboarding_completed": False,
        "missing_fields": ["business_name", "industry", "description", "business_model", "sales_channels"],
        "next_step": "create_business_profile",
    }
    assert client.get("/api/v1/auth/me", headers=auth_headers).json()["onboarding_completed"] is False


def test_full_signup_then_onboarding_flow(client):
    # 1. account first
    r = client.post("/api/v1/auth/register", json={"email": "flow@example.com", "password": "Passw0rd123"})
    assert r.status_code == 201
    assert "onboarding_completed" not in r.json()
    # 2. login
    r = client.post("/api/v1/auth/login", data={"username": "flow@example.com", "password": "Passw0rd123"})
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert client.get("/api/v1/auth/me", headers=headers).json()["onboarding_completed"] is False
    # 3. portfolio saved under the authenticated user
    r = client.put("/api/v1/business-profile", json=PROFILE, headers=headers)
    assert r.status_code == 200
    # 4. done
    status = client.get("/api/v1/onboarding/status", headers=headers).json()
    assert status["onboarding_completed"] is True and status["next_step"] == "done"
    assert status["missing_fields"] == []
    assert client.get("/api/v1/auth/me", headers=headers).json()["onboarding_completed"] is True


def test_incomplete_profile_can_be_resumed(client, auth_headers, session_factory):
    """A profile saved before the new fields existed shows as incomplete and can be finished."""
    me = client.get("/api/v1/auth/me", headers=auth_headers).json()
    with session_factory() as db:
        db.add(BusinessProfile(user_id=me["id"], business_name="Old Shop", industry="Home goods", sales_channels=["Etsy"]))
        db.commit()

    r = client.get("/api/v1/business-profile", headers=auth_headers)
    assert r.status_code == 200  # legacy row is readable, not a 500
    assert r.json()["onboarding_completed"] is False
    legacy_id = r.json()["id"]
    status = client.get("/api/v1/onboarding/status", headers=auth_headers).json()
    assert status["profile_exists"] is True
    assert status["next_step"] == "complete_business_profile"
    assert status["missing_fields"] == ["description", "business_model"]

    r = client.put("/api/v1/business-profile", json=PROFILE, headers=auth_headers)
    assert r.status_code == 200 and r.json()["id"] == legacy_id  # completed in place, no duplicate
    assert client.get("/api/v1/onboarding/status", headers=auth_headers).json()["next_step"] == "done"


def test_onboarding_status_requires_auth_and_is_per_user(client, auth_headers, other_headers):
    assert client.get("/api/v1/onboarding/status").status_code == 401
    client.put("/api/v1/business-profile", json=PROFILE, headers=auth_headers)
    assert client.get("/api/v1/onboarding/status", headers=auth_headers).json()["onboarding_completed"] is True
    assert client.get("/api/v1/onboarding/status", headers=other_headers).json()["onboarding_completed"] is False


def test_business_context_helper_for_future_ai_modules(client, auth_headers, session_factory):
    client.put("/api/v1/business-profile", json={**PROFILE, "goals": None}, headers=auth_headers)
    me = client.get("/api/v1/auth/me", headers=auth_headers).json()
    with session_factory() as db:
        ctx = get_business_context_for_user(db, me["id"])
    assert ctx["business_name"] == "Cozy Candles"
    assert ctx["sales_channels"] == ["marketplace", "social_commerce"]
    assert "goals" not in ctx  # empty fields are left out
    assert "user_id" not in ctx and "id" not in ctx  # no identifiers or credentials
    assert build_business_context(None) == {}
