PRODUCT = {"name": "Lavender Candle", "category": "Candles", "price": 12.5, "inventory_count": 10}


def create(client, headers, **overrides):
    r = client.post("/api/v1/products", json={**PRODUCT, **overrides}, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_product_crud(client, auth_headers):
    p = create(client, auth_headers)
    assert p["price"] == 12.5 and p["name"] == "Lavender Candle"

    r = client.get(f"/api/v1/products/{p['id']}", headers=auth_headers)
    assert r.status_code == 200 and r.json()["id"] == p["id"]

    create(client, auth_headers, name="Vanilla Candle", category="Candles")
    create(client, auth_headers, name="Mug", category="Kitchen", price=8)
    r = client.get("/api/v1/products", headers=auth_headers)
    assert len(r.json()) == 3
    r = client.get("/api/v1/products?category=Kitchen", headers=auth_headers)
    assert [x["name"] for x in r.json()] == ["Mug"]

    r = client.patch(f"/api/v1/products/{p['id']}", json={"price": 15, "description": "Soy wax"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["price"] == 15 and r.json()["description"] == "Soy wax"
    assert r.json()["name"] == "Lavender Candle"  # untouched field preserved

    assert client.delete(f"/api/v1/products/{p['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/v1/products/{p['id']}", headers=auth_headers).status_code == 404


def test_product_validation(client, auth_headers):
    for bad in [{"price": 0}, {"price": -1}, {"inventory_count": -1}, {"name": ""}]:
        r = client.post("/api/v1/products", json={**PRODUCT, **bad}, headers=auth_headers)
        assert r.status_code == 422, bad
    p = create(client, auth_headers)
    r = client.patch(f"/api/v1/products/{p['id']}", json={"price": -5}, headers=auth_headers)
    assert r.status_code == 422
    r = client.patch(f"/api/v1/products/{p['id']}", json={"name": None}, headers=auth_headers)
    assert r.status_code == 422


def test_inventory_optional(client, auth_headers):
    r = client.post("/api/v1/products", json={"name": "X", "category": "Y", "price": 1}, headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["inventory_count"] is None


def test_client_supplied_user_id_is_ignored(client, auth_headers):
    me = client.get("/api/v1/auth/me", headers=auth_headers).json()
    p = create(client, auth_headers, user_id=9999)
    assert p["user_id"] == me["id"]


def test_cross_user_access_prevented(client, auth_headers, other_headers):
    p = create(client, auth_headers)
    url = f"/api/v1/products/{p['id']}"
    assert client.get(url, headers=other_headers).status_code == 404
    assert client.patch(url, json={"price": 1}, headers=other_headers).status_code == 404
    assert client.delete(url, headers=other_headers).status_code == 404
    assert client.get("/api/v1/products", headers=other_headers).json() == []
    # Owner's product is untouched
    r = client.get(url, headers=auth_headers)
    assert r.status_code == 200 and r.json()["price"] == 12.5


def test_nonexistent_product_404(client, auth_headers):
    assert client.get("/api/v1/products/99999", headers=auth_headers).status_code == 404
