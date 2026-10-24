# Strategy / Recommendation API contract (Member 4 -> Member 1)

Base: `/api/v1`. All endpoints need the seller's login. Timestamps are UTC, ISO-8601 with `Z`.
`null` means "missing / not recorded", **never** zero. Errors look like `{"detail": "message"}`.

## Status values (final)
`proposed | approved | edited | ignored | executed`

## action_type values
`promote_product | improve_before_promoting | collect_more_data`

## score_interpretation values
`high | medium | low | limited_evidence | insufficient_evidence`

## Endpoints
| Method + path | Purpose | Success |
|---|---|---|
| POST `/strategy/generate` | body optional: `{"max_recommendations": 1..10}` | 201 StrategyRun |
| GET `/strategy/runs?limit=20&offset=0` | list runs (summary, newest first) | 200 |
| GET `/strategy/runs/{run_id}` | one run with recommendations | 200 / 404 |
| GET `/recommendations?status=&run_id=&limit=50&offset=0` | list | 200 |
| GET `/recommendations/{id}` | one | 200 / 404 |
| PATCH `/recommendations/{id}` | body: any of `status`, `title`, `suggested_content` (at least one) | 200 / 404 / 422 |
| POST `/recommendations/{id}/outcome` | body: `notes`, `reach`, `clicks`, `orders` (all optional, >= 0) | 201 Recommendation |
| GET `/dashboard/summary` | counts + top 3 of latest run | 200 |

Editing `title`/`suggested_content` without a `status` sets status to `edited`.
Recording an outcome sets status to `executed`.
Other errors: 400 (no products), 401 (not logged in), 404 (not found OR belongs to another seller), 500 (could not save).

## Example: POST /strategy/generate -> 201
```json
{
  "id": 1,
  "created_at": "2026-10-21T10:30:00Z",
  "llm_provider": "mock",
  "used_fallback": false,
  "data_warnings": ["Demo data is being used (fixture), not real seller data."],
  "weights_used": {"performance": 0.35, "customer_interest": 0.3, "demand": 0.2, "context": 0.15},
  "recommendations": [
    {
      "id": 1, "strategy_run_id": 1, "target_product_id": 1,
      "title": "Promote Handmade Candle Set first",
      "action_type": "promote_product", "priority": 1,
      "score": 70.1, "score_interpretation": "high",
      "reasoning_summary": "Handmade Candle Set has an opportunity score of 70.1 out of 100 (high). Its engagement rate is 7.0%.",
      "supporting_evidence": ["Engagement rate: 7.0%", "Positive feedback: 72.0% (based on 14 feedback entries)", "Opportunity score: 70.1/100 (high)"],
      "suggested_content": "Short video or reel showing Handmade Candle Set in everyday use...",
      "data_gaps": [],
      "caveats": ["Opportunity scores use initial weights that are design assumptions, not validated predictions."],
      "status": "proposed",
      "created_at": "2026-10-21T10:30:00Z", "updated_at": "2026-10-21T10:30:00Z",
      "outcomes": []
    }
  ]
}
```
`supporting_evidence` = measured facts. `reasoning_summary` / `suggested_content` = generated wording
(show them as "suggestion", visually separate from the facts).
If `used_fallback` is true, show `data_warnings` to the seller.
