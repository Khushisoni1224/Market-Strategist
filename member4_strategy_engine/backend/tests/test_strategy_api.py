import json

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from tests.conftest import USER_1, USER_2, FailingProvider, FixedProvider


def generate(client, headers=USER_1, body=None):
    return client.post("/api/v1/strategy/generate", json=body, headers=headers)


# ---------------------------------------------------------------- generate
def test_generate_requires_login(client):
    assert client.post("/api/v1/strategy/generate").status_code == 401


def test_generate_works_with_mock_provider_and_no_api_key(client):
    r = generate(client)
    assert r.status_code == 201
    body = r.json()
    assert body["llm_provider"] == "mock"
    assert body["used_fallback"] is False
    recs = body["recommendations"]
    assert [x["priority"] for x in recs] == [1, 2, 3, 4]
    assert recs[0]["target_product_id"] == 1
    assert recs[0]["action_type"] == "promote_product"
    scores = [x["score"] for x in recs[:3]]
    assert scores == sorted(scores, reverse=True)
    last = recs[-1]
    assert last["score"] is None and last["action_type"] == "collect_more_data"
    for rec in recs:
        assert rec["supporting_evidence"] and rec["caveats"]
        assert rec["status"] == "proposed"


def test_missing_data_is_reported_not_zeroed(client):
    recs = generate(client).json()["recommendations"]
    soap = [x for x in recs if x["target_product_id"] == 3][0]
    assert "customer_interest" in soap["data_gaps"]
    assert any("not recorded" in fact for fact in soap["supporting_evidence"])


def test_max_recommendations_is_respected(client):
    recs = generate(client, body={"max_recommendations": 1}).json()["recommendations"]
    assert len(recs) == 2          # 1 scored + the "collect more data" item


def test_max_recommendations_validation(client):
    assert generate(client, body={"max_recommendations": 0}).status_code == 422


# ---------------------------------------------------------------- AI failure handling
def test_provider_failure_falls_back_gracefully(make_client):
    r = generate(make_client(FailingProvider()))
    assert r.status_code == 201
    body = r.json()
    assert body["used_fallback"] is True
    assert any("unavailable" in w for w in body["data_warnings"])
    assert body["recommendations"][0]["reasoning_summary"]


def test_invalid_json_from_ai_falls_back(make_client):
    body = generate(make_client(FixedProvider("sorry, I can't"))).json()
    assert body["used_fallback"] is True


def test_invented_numbers_from_ai_fall_back(make_client):
    bad = json.dumps({"recommendations": [{
        "product_id": 1, "title": "Promote", "reasoning_summary": "Sales grew 450% last week.",
        "suggested_content": "x", "evidence_used": [], "caveats": []}]})
    body = generate(make_client(FixedProvider(bad))).json()
    assert body["used_fallback"] is True
    assert "450" not in json.dumps(body)


def test_database_failure_returns_controlled_error(client, monkeypatch):
    def boom(self):
        raise SQLAlchemyError("secret internal detail")
    monkeypatch.setattr(Session, "commit", boom)
    r = generate(client)
    assert r.status_code == 500
    assert "secret internal detail" not in r.text
    assert "Could not save" in r.json()["detail"]


# ---------------------------------------------------------------- history + ownership
def test_runs_history_and_detail(client):
    run_id = generate(client).json()["id"]
    listing = client.get("/api/v1/strategy/runs", headers=USER_1).json()
    assert [x["id"] for x in listing] == [run_id]
    detail = client.get(f"/api/v1/strategy/runs/{run_id}", headers=USER_1)
    assert detail.status_code == 200 and len(detail.json()["recommendations"]) == 4


def test_other_seller_cannot_see_my_data(client):
    run_id = generate(client).json()["id"]
    rec_id = client.get("/api/v1/recommendations", headers=USER_1).json()[0]["id"]

    assert client.get("/api/v1/strategy/runs", headers=USER_2).json() == []
    assert client.get(f"/api/v1/strategy/runs/{run_id}", headers=USER_2).status_code == 404
    assert client.get("/api/v1/recommendations", headers=USER_2).json() == []
    assert client.get(f"/api/v1/recommendations/{rec_id}", headers=USER_2).status_code == 404
    assert client.patch(f"/api/v1/recommendations/{rec_id}", json={"status": "approved"},
                        headers=USER_2).status_code == 404
    assert client.post(f"/api/v1/recommendations/{rec_id}/outcome", json={"notes": "x"},
                       headers=USER_2).status_code == 404


def test_unknown_ids_return_404(client):
    assert client.get("/api/v1/strategy/runs/999", headers=USER_1).status_code == 404
    assert client.get("/api/v1/recommendations/999", headers=USER_1).status_code == 404


# ---------------------------------------------------------------- seller control
def first_rec_id(client):
    generate(client)
    return client.get("/api/v1/recommendations", headers=USER_1).json()[0]["id"]


def test_approve_ignore_and_execute(client):
    rec_id = first_rec_id(client)
    for status in ("approved", "ignored", "executed"):
        r = client.patch(f"/api/v1/recommendations/{rec_id}", json={"status": status}, headers=USER_1)
        assert r.status_code == 200 and r.json()["status"] == status


def test_editing_text_marks_recommendation_as_edited(client):
    rec_id = first_rec_id(client)
    r = client.patch(f"/api/v1/recommendations/{rec_id}",
                     json={"title": "My own title", "suggested_content": "My own idea"}, headers=USER_1)
    body = r.json()
    assert body["status"] == "edited" and body["title"] == "My own title"


def test_patch_needs_at_least_one_field_and_valid_status(client):
    rec_id = first_rec_id(client)
    assert client.patch(f"/api/v1/recommendations/{rec_id}", json={}, headers=USER_1).status_code == 422
    assert client.patch(f"/api/v1/recommendations/{rec_id}", json={"status": "nonsense"},
                        headers=USER_1).status_code == 422


def test_list_filter_by_status(client):
    rec_id = first_rec_id(client)
    client.patch(f"/api/v1/recommendations/{rec_id}", json={"status": "approved"}, headers=USER_1)
    approved = client.get("/api/v1/recommendations?status=approved", headers=USER_1).json()
    proposed = client.get("/api/v1/recommendations?status=proposed", headers=USER_1).json()
    assert [x["id"] for x in approved] == [rec_id]
    assert rec_id not in [x["id"] for x in proposed]


def test_record_outcome_marks_executed_and_keeps_none(client):
    rec_id = first_rec_id(client)
    r = client.post(f"/api/v1/recommendations/{rec_id}/outcome",
                    json={"notes": "Posted a reel", "orders": 2}, headers=USER_1)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "executed"
    outcome = body["outcomes"][0]
    assert outcome["orders"] == 2 and outcome["reach"] is None and outcome["clicks"] is None


def test_outcome_rejects_negative_numbers(client):
    rec_id = first_rec_id(client)
    r = client.post(f"/api/v1/recommendations/{rec_id}/outcome", json={"reach": -5}, headers=USER_1)
    assert r.status_code == 422


# ---------------------------------------------------------------- dashboard
def test_dashboard_summary(client):
    empty = client.get("/api/v1/dashboard/summary", headers=USER_1).json()
    assert empty["latest_run_id"] is None and empty["total_runs"] == 0

    generate(client)
    summary = client.get("/api/v1/dashboard/summary", headers=USER_1).json()
    assert summary["total_runs"] == 1
    assert summary["status_counts"]["proposed"] == 4
    assert len(summary["top_recommendations"]) == 3
