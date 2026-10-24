"""Test setup: runs against an isolated in-memory SQLite database.

The env vars below are set BEFORE the app is imported, so tests can never touch
your development PostgreSQL database.
"""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-only-secret-key-not-for-real-use-0123456789"
os.environ["AUTO_CREATE_TABLES"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models  # noqa: E402,F401
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

PASSWORD = "Passw0rd123"

PROFILE = {
    "business_name": "Cozy Candles",
    "industry": "Home decor",
    "description": "Hand-poured soy candles sold to gift buyers.",
    "business_model": "product",
    "sales_channels": ["marketplace", "social_commerce"],
    "target_audience": "Gift buyers aged 25-40",
    "website_url": "https://cozycandles.example.com",
    "location": "India",
    "goals": "Grow repeat customers",
}


@pytest.fixture()
def session_factory():
    """Raw DB access for tests that need to seed rows the API cannot create."""
    return _state["factory"]


_state: dict = {}


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    _state["factory"] = TestingSession

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def make_user_headers(client: TestClient, email: str) -> dict[str, str]:
    r = client.post("/api/v1/auth/register", json={"email": email, "password": PASSWORD})
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/auth/login", data={"username": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def auth_headers(client):
    return make_user_headers(client, "alice@example.com")


@pytest.fixture()
def other_headers(client):
    return make_user_headers(client, "bob@example.com")
