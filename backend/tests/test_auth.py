from tests.conftest import PASSWORD


def test_register_success_hides_password(client):
    r = client.post("/api/v1/auth/register", json={"email": "New@Example.com", "password": PASSWORD})
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "new@example.com"
    assert body["is_active"] is True
    assert "password" not in body and "hashed_password" not in body


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": PASSWORD}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    r = client.post("/api/v1/auth/register", json={**payload, "email": "DUP@example.com"})
    assert r.status_code == 409


def test_register_validation(client):
    assert client.post("/api/v1/auth/register", json={"email": "bad", "password": PASSWORD}).status_code == 422
    assert client.post("/api/v1/auth/register", json={"email": "a@example.com", "password": "short1"}).status_code == 422
    assert client.post("/api/v1/auth/register", json={"email": "a@example.com", "password": "onlyletters"}).status_code == 422


def test_login_success(client):
    client.post("/api/v1/auth/register", json={"email": "a@example.com", "password": PASSWORD})
    r = client.post("/api/v1/auth/login", data={"username": "a@example.com", "password": PASSWORD})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_login_failures(client):
    client.post("/api/v1/auth/register", json={"email": "a@example.com", "password": PASSWORD})
    wrong = client.post("/api/v1/auth/login", data={"username": "a@example.com", "password": "Wrong1234"})
    unknown = client.post("/api/v1/auth/login", data={"username": "nobody@example.com", "password": PASSWORD})
    assert wrong.status_code == 401
    assert unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_me_requires_auth(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    r = client.get("/api/v1/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "alice@example.com"


def test_expired_token_rejected(client, auth_headers):
    from app.core.security import create_access_token

    token = create_access_token(1, expires_minutes=-5)
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_protected_endpoints_require_auth(client):
    for method, url in [
        ("get", "/api/v1/business-profile"),
        ("put", "/api/v1/business-profile"),
        ("get", "/api/v1/products"),
        ("post", "/api/v1/products"),
        ("get", "/api/v1/products/1"),
        ("patch", "/api/v1/products/1"),
        ("delete", "/api/v1/products/1"),
    ]:
        assert getattr(client, method)(url).status_code == 401, (method, url)
