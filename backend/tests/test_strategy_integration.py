"""Integration smoke tests for the authenticated strategy engine."""
def test_strategy_routes_are_registered(client, auth_headers):
    response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total_runs"] == 0


def test_strategy_uses_real_seller_products_and_requires_jwt(client, auth_headers, other_headers):
    assert client.post("/api/v1/strategy/generate").status_code == 401

    created = client.post(
        "/api/v1/products",
        headers=auth_headers,
        json={
            "name": "Test Candle",
            "category": "Home decor",
            "price": 12.5,
            "description": "A hand-poured candle for gifts.",
            "inventory_count": 10,
        },
    )
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]

    generated = client.post("/api/v1/strategy/generate", headers=auth_headers, json={})
    assert generated.status_code == 201, generated.text
    payload = generated.json()
    assert payload["recommendations"]
    assert payload["recommendations"][0]["target_product_id"] is None
    assert any("not stored in the current data model" in warning for warning in payload["data_warnings"])

    # Seller B must not see Seller A's strategy history or recommendations.
    assert client.get("/api/v1/strategy/runs", headers=other_headers).json() == []
    assert client.get("/api/v1/recommendations", headers=other_headers).json() == []
