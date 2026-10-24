# Member 4: Strategy Engine (scoring, AI strategy, recommendations, history)

Branch: `feature/member-4-strategy-engine`

## What this is
Takes seller evidence -> scores each product with maths -> asks an AI (or the mock) to word the
advice -> validates the AI answer -> saves ranked, explainable recommendations -> seller approves /
edits / ignores / marks executed -> history + outcomes.

> Maths decides numbers, ranking and action type. The AI only writes wording. It cannot invent metrics
> (the validator rejects answers containing numbers that are not in the evidence).

## Run it on your computer (needs Python 3.10+)
```
cd backend
python -m venv venv
venv\Scripts\activate            # Windows        (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
pytest                           # all tests should pass
uvicorn app.main:app --reload
```
Open http://localhost:8000/docs . For every request fill the `x-user-id` box with `1`
(that is the TEMPORARY fake login). Then try, in order:
1. `POST /api/v1/strategy/generate`  (Try it out -> Execute)
2. `GET  /api/v1/recommendations`
3. `PATCH /api/v1/recommendations/{id}`  body: `{"status": "approved"}`
4. `POST /api/v1/recommendations/{id}/outcome`  body: `{"notes": "Posted a reel", "orders": 2}`
5. `GET  /api/v1/strategy/runs` and `GET /api/v1/dashboard/summary`

## Which files are YOURS (commit these in your PR)
```
backend/app/models/strategy.py            backend/app/services/strategy_service.py
backend/app/models/recommendation.py      backend/app/services/scoring_service.py
backend/app/models/__init__.py (ask M2)   backend/app/services/prompt_builder.py
backend/app/schemas/strategy.py           backend/app/services/llm_provider.py
backend/app/schemas/recommendation.py     backend/app/services/response_validator.py
backend/app/api/v1/endpoints/strategy.py  backend/app/services/recommendation_service.py
backend/app/api/v1/endpoints/recommendations.py   backend/app/services/errors.py
backend/app/api/v1/endpoints/dashboard.py (coordinate)  backend/app/services/evidence.py
backend/tests/test_*.py + conftest.py     docs/API_CONTRACT_STRATEGY.md
```

## TEMPORARY scaffolding: do NOT commit (other members own the real ones)
`app/main.py`, `app/core/config.py`, `app/db/base.py`, `app/db/session.py`,
`app/api/v1/router.py`, `requirements.txt`, `pytest.ini`, `.env.example`,
and the fake-login + fixture parts of `app/api/deps.py`.

## Integration to-do list (when the others finish)
| When | What to do |
|---|---|
| Member 2 has the backend | Ask them to register your 3 routers in their `router.py`, add your models to Alembic, and tell you the names of their `get_db`, `Base`, `settings`, and "current user" dependency. Adjust the 3-4 import lines in your files to match. Add a real foreign key `owner_id -> users.id`. |
| Member 2 has auth | In `deps.py`, replace `get_current_user_id` with their dependency (must return the seller's integer id). |
| Member 2 has products | Product names/ids come from their `products` endpoints/service. |
| Member 3 has insights | Write a class with `load(owner_id) -> EvidenceBundle` that calls their services and fills `ProductEvidence` (keep missing = `None`, never 0). Return it from `get_evidence_source` in `deps.py`. Delete nothing else. |
| Real AI wanted | In your private `.env`: `LLM_PROVIDER=openai`, `LLM_API_KEY=...`, `LLM_MODEL=...`. Never commit `.env`. |

## Scoring in one paragraph
Each product gets four 0-100 signals: performance (engagement rate; 10 % = 100), customer interest
(positive feedback share), demand (enquiries + requests; 20 = 100), context (seasonality 0-100).
Final score = weighted average with weights 35/30/20/15. Missing signals are dropped and the remaining
weights re-scaled to total 1. Weights are design assumptions (not validated); change them with
`SCORING_WEIGHTS_JSON`. Score >= 70 high, >= 40 medium, else low; one signal only = "limited evidence".

## Known limitations (put these in your PR)
* Normalisation constants (10 %, 20, thresholds) are assumptions, documented in `scoring_service.py`.
* The number check in the validator is a safety net, not a proof that every AI sentence is true.
* `OpenAICompatibleProvider` needs a real key to try; everything else works without one.
* Uses fixture evidence until Member 2/3 integration.
