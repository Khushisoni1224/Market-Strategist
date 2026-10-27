# Member 3 Backend Integration Guide
## AI-Powered E-Commerce Marketing Strategist for Small Businesses

**Purpose:** Explain how Member 3's backend files connect, how requests flow through the API, how data is stored, and how other team members can integrate with the module.

**Repository:** `Market-Strategist`  
**Member 3 branch:** `feature/member-3-data-intelligence`  
**Last previously confirmed commit:** `d71718a` — `Implement Member 3 feedback and marketing analytics`  
**Backend directory:** `backend/`

> **Integration status note:** This guide reflects the Member 3 backend implementation previously reviewed. The implementation had feedback, marketing, and analytics-summary routes, and the backend test suite last reported 63 passed and 1 warning. The latest requirements specify additional route names and response features. Do not assume every route listed in the “Required but not yet confirmed” section exists until the current branch is inspected and tested.

---

## 1. High-level architecture

The backend uses:

- **FastAPI** for HTTP endpoints.
- **Pydantic 2** for request and response validation.
- **SQLAlchemy 2.x** for database models and queries.
- **Alembic** for schema migrations.
- **PostgreSQL with psycopg** for shared/deployed environments.
- **SQLite** for isolated automated tests and optional local development.
- **JWT authentication** through the existing application auth dependencies.
- **VADER Sentiment** for review sentiment scoring.
- Python's built-in `csv` module for CSV imports; pandas is not required for these import flows.

### Request-to-database flow

```text
React frontend / API client
        |
        | HTTP request + Authorization: Bearer <JWT>
        v
FastAPI application: app/main.py
        |
        v
API v1 router: app/api/v1/router.py
        |
        +--> Feedback endpoints
        +--> Marketing endpoints
        +--> Analytics endpoints
        |
        | CurrentUser validates the caller
        | DbSession provides a SQLAlchemy session
        v
Endpoint: validate request, apply filters, enforce ownership
        |
        +--> Pydantic schema: response validation/serialization
        |
        +--> Service layer: import, sentiment, themes, metrics, analytics
        |
        v
SQLAlchemy models and database session
        |
        v
Database tables
```

**Important:** The frontend must not supply a trusted `user_id` to select whose data to read or write. The backend gets the user identity from `CurrentUser` and uses that identity in database queries.

---

## 2. Main folder structure

The Member 3 files are in the following locations:

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── dependencies.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── feedback_import.py
│   │   ├── customer_feedback.py
│   │   ├── marketing_import.py
│   │   └── marketing_performance.py
│   ├── schemas/
│   │   ├── feedback.py
│   │   ├── marketing.py
│   │   └── analytics.py
│   ├── services/
│   │   ├── pii.py
│   │   ├── sentiment_service.py
│   │   ├── complaint_service.py
│   │   ├── feedback_import.py
│   │   ├── marketing_import.py
│   │   ├── marketing_metrics.py
│   │   └── analytics_snapshot.py
│   └── api/
│       └── v1/
│           ├── router.py
│           └── endpoints/
│               ├── feedback.py
│               ├── marketing.py
│               └── analytics.py
├── alembic/
│   └── versions/
│       └── 0003_data_intelligence_tables.py
├── tests/
│   ├── conftest.py
│   ├── test_feedback.py
│   ├── test_marketing.py
│   ├── test_marketing_import_service.py
│   ├── test_marketing_metrics.py
│   ├── test_analytics.py
│   └── test_analytics_snapshot.py
├── requirements.txt
├── alembic.ini
└── README.md
```

The actual repository may contain additional files. This is the Member 3-related layout previously reviewed, not a guarantee that every filename matches the latest requested layout exactly.

### Why the requested layout may differ

The latest specification requests `app/models/feedback.py` and `app/models/marketing.py`. The implementation previously reviewed instead uses separate model files:

- `app/models/feedback_import.py`
- `app/models/customer_feedback.py`
- `app/models/marketing_import.py`
- `app/models/marketing_performance.py`

Do not rename these files only to match a diagram without updating imports, tests, and migrations consistently.

---

## 3. Application startup and routing

### `app/main.py`

This is the FastAPI application entry point. Uvicorn imports the app from this module.

Local development command, run from `backend/`:

```cmd
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Local API documentation:

- Swagger UI: `http://127.0.0.1:8001/docs`
- ReDoc: `http://127.0.0.1:8001/redoc`

These addresses are local to the developer's computer; they are not public deployment URLs.

### `app/api/v1/router.py`

This file assembles the version 1 API router and includes the feature routers. Member 3 routes should be registered here with one `include_router(...)` line per feature router, under the Member 3 section.

Conceptually:

```python
api_router.include_router(feedback.router)
api_router.include_router(marketing.router)
api_router.include_router(analytics.router)
```

The exact prefixes and tags are defined by the individual routers. The app's main module mounts the API v1 router under `/api/v1`.

**Integration rule:** Keep Member 2's routers and files unchanged. Add or update Member 3's routes in Member 3's endpoint files and register them in the API router.

---

## 4. Authentication, configuration, and database session

### `app/core/dependencies.py`

This module provides shared endpoint dependencies, including:

- `CurrentUser`: resolves the authenticated user from the JWT.
- `DbSession`: provides a SQLAlchemy database session.

Member 3 endpoints should use both dependencies. For example, conceptually:

```python
def some_endpoint(
    current_user: CurrentUser,
    db: DbSession,
):
    ...
```

Use the actual type aliases already defined by the project. Do not implement a separate authentication mechanism for the analytics features.

### `app/core/config.py`

Reads application settings from environment variables and the backend `.env` file. Important settings include:

- `DATABASE_URL`
- `SECRET_KEY`
- token expiration
- environment/CORS settings
- `AUTO_CREATE_TABLES`

Never commit `.env`, passwords, or real secret keys. Shared environments should use their approved PostgreSQL configuration.

### `app/db/session.py`

Creates the SQLAlchemy engine and session factory from the configured database URL. Endpoints receive sessions through `DbSession`; they should not create a new engine per request.

### `app/db/base.py`

Defines the shared SQLAlchemy declarative `Base` and naming conventions for database constraints. Member 3 models inherit this `Base`, and check constraints should have explicit names.

---

## 5. Database models and relationships

### Model overview

| Model | Purpose | Main relationship |
|---|---|---|
| `FeedbackImport` | Tracks each feedback CSV import attempt | One import has many `CustomerFeedback` rows |
| `CustomerFeedback` | Stores a masked review and its saved sentiment/theme results | Belongs to a user and import; may reference a product |
| `MarketingImport` | Tracks each marketing CSV import attempt | One import can create/update many performance rows |
| `MarketingPerformance` | Stores content performance metrics by date and content ID | Belongs to a user and import; may reference a product |

### Relationship diagram

```text
users
  |
  +----< feedback_imports
  |           |
  |           +----< customer_feedback >---- products (optional)
  |
  +----< marketing_imports
  |           |
  |           +----< marketing_performance >---- products (optional)
  |
  +----< products
```

`users` and `products` are existing application tables owned by the core project. Member 3 must use the existing models and must not create duplicate user/product systems.

### `FeedbackImport`

Tracks feedback import attempts and summary counts/status. The latest specification names `total_rows`, `valid_count`, and `invalid_count`; the previously reviewed implementation uses `total_rows`, `saved_rows`, and `failed_rows`. Confirm the actual current model and response schema before relying on field names.

### `CustomerFeedback`

Stores one imported review. Key data includes:

- `user_id` — owner of the record.
- `feedback_import_id` (called `import_id` in the latest specification) — associated import.
- `review_text` — text after masking personal information.
- `rating` — nullable rating, validated to the allowed range.
- `sentiment` and `sentiment_score` — computed once during import.
- `themes` — saved theme list.
- `product_id` — optional link to the user's own product.
- `created_at` and row metadata where supported.

Sentiment and themes should be computed at import time and stored. Dashboard requests should use the stored values rather than re-score all reviews.

### `MarketingImport`

Tracks the marketing import attempt and its status/counts. The latest specification expects `saved_count`, `updated_count`, and `invalid_count`; the previously reviewed implementation used `saved_rows`, `updated_rows`, and `invalid_rows`.

### `MarketingPerformance`

Stores performance values for a content item and date. The latest specification includes nullable non-negative metrics such as reach, impressions, views, likes, comments, saves, shares, profile visits, clicks, enquiries, and conversions.

The previously reviewed implementation had a smaller metric set. Before frontend integration, compare the actual model to the latest specification.

The intended upsert key is:

```text
(user_id, content_date, content_id)
```

Re-uploading the same content/date for the same user should update the row rather than create a duplicate. Records belonging to another user must never be updated.

### Tenancy and ownership

All Member 3 queries must be scoped to the authenticated user's ID. A record ID by itself is not sufficient to prove ownership.

For an individual resource, query by both its identifier and the current user's ID. If the record does not belong to the caller or does not exist, return 404 where the endpoint's contract calls for an individual-resource lookup.

---

## 6. Service layer: how the files connect

The service layer contains business logic that endpoints call. It should not be duplicated inside React components or repeated across endpoint handlers.

### `services/pii.py`

Provides the shared personal-information masking helper, `mask_personal_information()`, for email addresses and phone numbers.

Used by:
- single-review analysis
- feedback CSV import

The API should not return unmasked imported review text if the contract requires masking.

### `services/sentiment_service.py`

Uses VADER to produce a sentiment score and label. The VADER analyzer should be reused (module-level or cached), not recreated for each review.

Previously used thresholds:

- compound score `>= 0.05` → `Positive`
- compound score `<= -0.05` → `Negative`
- otherwise → `Neutral`

The response may include the compound score and positive/neutral/negative component scores, depending on the endpoint schema.

### `services/complaint_service.py`

Keeps complaint-theme patterns in one place and detects themes for negative reviews only. Each review should contribute at most once to a particular theme. Avoid ambiguous or overlapping generic words that cause false positives.

### `services/feedback_import.py`

Coordinates the feedback CSV workflow:

1. Validate file size and CSV structure.
2. Decode UTF-8 with BOM, falling back to cp1252 if required.
3. Validate headers and row count.
4. Require `Review Text`; treat `Rating` and `Product` as optional according to the specification.
5. Mask personal information.
6. Compute sentiment and complaint themes once.
7. Match a supplied product name against the current user's own products, case-insensitively.
8. Store import history and review rows.
9. Return counts and clear validation/row error information.

Import safeguards in the specification include a 5 MB file limit and a 10,000-row limit. Check that these remain present in the current code.

### `services/marketing_import.py`

Coordinates the marketing CSV workflow:

1. Validate file size, decoding, headers, dates and metrics.
2. Treat blank metrics as `NULL`, not zero.
3. Reject negative or nonnumeric metrics as invalid rows.
4. Partially accept valid rows while reporting invalid row numbers (maximum 50 in the response).
5. Match `product_name` to the current user's own products, if possible.
6. Upsert by `(user_id, content_date, content_id)`.
7. Track saved, updated and invalid counts and the import status.

The required behavior is to record every attempt, including failures, and move the import status through `processing` to `completed` or `failed` as appropriate. Verify transaction boundaries in the actual code before relying on this guarantee.

### `services/marketing_metrics.py`

Contains shared calculations for marketing rates, so list and summary endpoints use the same definitions. The previously reviewed implementation calculated:

- CTR = clicks / impressions × 100
- Conversion rate = conversions / clicks × 100
- Engagement rate = (likes + comments + shares) / reach × 100

A rate must be unavailable (`null`/`N/A` in the UI) if its required data is missing or its denominator is zero. Do not silently treat missing values as zero.

The latest specification adds more metrics; confirm whether the exact engagement-rate definition should include saves or other interactions before frontend charts are finalized.

### `services/analytics_snapshot.py`

Provides a read-only summary function for other backend features, especially Member 4. The intended function is:

```python
get_analytics_snapshot(db, user_id) -> dict
```

The latest requirements expect it to provide data such as top complaint themes, sentiment percentages, average rating, best content type, best product by conversions, and data completeness. It should not call an AI service or generate marketing recommendations.

The previously reviewed implementation returned a feedback/marketing summary, but the complete latest snapshot shape must be checked against the actual function and schemas.

---

## 7. Pydantic schemas

Schemas describe what the API accepts and returns. They are separate from SQLAlchemy database models.

| Schema file | Responsibility |
|---|---|
| `app/schemas/feedback.py` | Feedback rows, import history/results, paginated feedback responses |
| `app/schemas/marketing.py` | Marketing performance rows, import history/results, paginated marketing responses |
| `app/schemas/analytics.py` | Aggregated feedback, marketing, and combined dashboard responses |

Endpoint handlers should declare response models. This validates output shape and gives the frontend a stable contract.

**Frontend rule:** TypeScript interfaces should mirror the actual Pydantic response models. Do not guess field names such as `saved_count` versus `saved_rows`, or `import_id` versus `feedback_import_id`. Confirm them from the running OpenAPI document or the schemas before writing the UI.

---

## 8. Endpoint files and request flow

### `endpoints/feedback.py`

Previously confirmed routes:

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/v1/feedback/import` | Upload/import feedback CSV |
| GET | `/api/v1/feedback` | List feedback with supported filters and pagination |
| GET | `/api/v1/feedback/imports` | List feedback import history |

The endpoint calls `feedback_import.py` for import processing, then queries the feedback models for list/history responses. It should use `CurrentUser` and `DbSession` and scope every query to the authenticated user.

### `endpoints/marketing.py`

Previously confirmed routes:

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/v1/marketing/import` | Upload/import marketing CSV |
| GET | `/api/v1/marketing` | List performance records with supported filters and pagination |
| GET | `/api/v1/marketing/imports` | List marketing import history |

The import endpoint calls `marketing_import.py`; list endpoints query `MarketingPerformance` and use `marketing_metrics.py` to calculate rates.

### `endpoints/analytics.py`

Previously confirmed route:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/v1/analytics/summary` | Return the combined analytics summary implemented at the time of review |

It calls `analytics_snapshot.py` and serializes the result through an analytics Pydantic schema.

### Routes required by the latest specification but not previously confirmed

The latest requirements call for the following additional route contracts:

| Method | Required route | Purpose |
|---|---|---|
| POST | `/api/v1/feedback/analyze` | Analyze one review and return masked text plus sentiment |
| POST | `/api/v1/feedback/imports` | Upload feedback CSV |
| GET | `/api/v1/feedback/imports/{id}` | Import detail, summary and paginated rows |
| GET | `/api/v1/feedback/summary` | Feedback KPIs, sentiment split, top themes and rating distribution |
| POST | `/api/v1/marketing/imports` | Upload marketing CSV |
| GET | `/api/v1/marketing/summary` | Marketing KPIs, totals and rates with filters |
| GET | `/api/v1/marketing/timeseries` | Daily reach/clicks/conversions |
| GET | `/api/v1/marketing/breakdown` | Breakdown by product and content type |
| GET | `/api/v1/analytics/overview` | Combined dashboard payload and up to three structured insights |

The older `/feedback/import`, `/marketing/import`, and `/analytics/summary` routes differ from the latest required paths. Coordinate with the backend owner before using these in the frontend. Either implement the specified routes or explicitly agree on the route contract with the team.

---

## 9. API conventions for frontend integration

### Authentication

Send the existing JWT in the request header:

```http
Authorization: Bearer <access_token>
```

Use the token provided by the existing login/auth flow. Do not hardcode a token in the analytics feature.

### Pagination

The project convention is:

- `skip`: integer greater than or equal to 0
- `limit`: integer from 1 through 200
- default `limit`: 50

For the frontend feedback table, request 10 records at a time if that is the desired UI page size.

### Filters

The latest requested filters are:

- Feedback: `sentiment`, `rating`, `product_id`, `import_id`
- Marketing: `start_date`, `end_date`, `product`, `content_type`

Confirm the actual query parameter names in OpenAPI before implementing the UI.

### Error handling

- `401`: missing or invalid authentication; use the existing app's login/session handling.
- `404`: requested individual record is missing or belongs to another user.
- `400`: invalid CSV/business validation, where specified.
- `422`: invalid query or request data according to FastAPI/Pydantic validation.

Display a user-friendly error in the UI. Never render server stack traces as page content.

### Missing/incomplete metrics

A metric or rate may be `null` when the source data is incomplete or the denominator is zero. Render `N/A` with a tooltip or explanatory label rather than displaying a misleading `0%`.

---

## 10. CSV formats

Confirm actual required headers from the current import service before preparing final template files. The intended formats are:

### Feedback CSV

Required:
- `Review Text`

Optional:
- `Rating`
- `Product`

Example:

```csv
Review Text,Rating,Product
"The fabric feels comfortable and the fit is good",5,Everyday T-Shirt
"The stitching came apart after one wash",2,Everyday T-Shirt
```

### Marketing CSV

The latest specification expects columns for date/content identity, content type and product name, plus nullable performance metrics. The exact date and identity header names must match the actual importer.

Illustrative shape (confirm headers against the implementation before use):

```csv
content_date,content_id,content_type,product_name,reach,impressions,views,likes,comments,saves,shares,profile_visits,clicks,enquiries,conversions
2026-10-20,post-001,Reel,Everyday T-Shirt,1200,1500,900,85,12,8,10,30,90,8,5
2026-10-21,post-002,Image,Everyday T-Shirt,800,1000,600,40,5,,4,12,35,3,2
```

A blank metric should remain `NULL`. Do not replace it with zero during CSV preparation. The example above is illustrative; use the sample/template CSV that matches the final importer.

### Import safety

The required safeguards are:
- maximum 5 MB per file
- maximum 10,000 data rows
- UTF-8 with BOM first, cp1252 fallback
- reject missing/duplicate headers and malformed structure
- validate dates and non-negative integer metrics
- partially accept valid marketing rows
- list at most 50 invalid-row details
- mask emails and phone numbers in feedback text
- match products only within the authenticated user's product records

---

## 11. Database migration and model registration

### Model registration

New SQLAlchemy models must be imported in `app/models/__init__.py`, so `Base.metadata` and Alembic can discover them.

### Migration history

The Member 3 migration was created as:

```text
alembic/versions/0003_data_intelligence_tables.py
revision = "0003"
down_revision = "0002"
```

Before applying it, verify that the migration graph has one expected head and that migration `0002` is present in the target database.

### Apply migration

Run from the `backend/` directory, after confirming the configured database URL points to the correct development/shared database:

```cmd
alembic heads
alembic current
alembic upgrade head
```

Do not run migrations against a production/shared database without the team's approval. Do not rely on `AUTO_CREATE_TABLES` to create the production schema; use Alembic migrations.

The local SQLite `dev.db` is a separate development database if configured through `DATABASE_URL=sqlite:///./dev.db`. It is not the same database as the Django Part A project.

---

## 12. Tests and integration checks

The backend test suite uses `tests/conftest.py` and an in-memory SQLite database. It should not connect to the local development database.

Run from `backend/`:

```cmd
.venv\Scripts\activate
python -m pytest -q
```

The last previously confirmed result was **63 passed, 1 warning**. Re-run the suite after code changes and record the current result; do not treat the old result as proof that future edits pass.

Important test areas:
- sentiment thresholds and PII masking
- feedback and marketing CSV validation
- blank metrics represented as `NULL`
- marketing upsert behavior
- rate calculations with zero/missing denominators
- product matching
- pagination
- authentication
- cross-user isolation
- analytics response shape

### OpenAPI check

With the backend running, open:

`http://127.0.0.1:8001/docs`

Use the documented paths to verify the live API. The OpenAPI document can also be viewed at:

`http://127.0.0.1:8001/openapi.json`

These URLs only work on the machine running the development server.

---

## 13. Frontend integration plan for Member 1

Before implementing Member 3's React screens:

1. Inspect the existing frontend's router, authentication context, API client, and UI/CSS library.
2. Reuse the existing auth flow and design system.
3. If there is no shared API client, add a small typed fetch wrapper that sends the JWT and handles `401`.
4. Create the analytics feature under `src/features/analytics/`.
5. Define TypeScript interfaces from the actual Pydantic schemas/OpenAPI output.
6. Implement loading, empty, success and error states.
7. Use real API data; do not hardcode dashboard metrics.
8. Confirm required endpoints exist before wiring screens to them.

Suggested frontend pages:
- **Overview:** KPI cards, daily performance chart, sentiment donut, top themes and up to three structured insights.
- **Feedback:** filters, sentiment badges, rating distribution and paginated reviews.
- **Marketing:** date/product/content-type filters, performance charts, best-performing post and paginated records.
- **Imports:** feedback/marketing CSV uploads, import results, error summaries and import history.

### API response contracts to agree on

Members 1 and 4 should use the final Pydantic schemas as the source of truth. In particular, agree on:
- import count names (`saved_count` vs `saved_rows`)
- import foreign key names (`import_id` vs `feedback_import_id`)
- whether rates are percentages or decimal fractions
- how incomplete aggregate metrics are represented
- exact shape of the combined overview response
- the exact route paths before frontend integration

Do not infer these details from this document alone if the code differs.

---

## 14. Integration responsibilities

### Member 3 — backend data intelligence
- Maintain the feedback/marketing models, import services, sentiment/theme analysis and aggregate endpoints.
- Keep all data access scoped to `CurrentUser`.
- Maintain migration and test coverage.
- Publish stable Pydantic response models and document the final route contract.

### Member 1 — frontend/core application
- Own the existing router, auth flow and shared frontend infrastructure.
- Reuse the shared API client and UI library.
- Integrate analytics pages without replacing authentication, onboarding, business profile or product features.

### Member 4 — downstream intelligence/recommendation
- Consume `analytics_snapshot.get_analytics_snapshot(db, user_id)` or its agreed stable service/API contract.
- Treat it as read-only data context.
- Do not assume the snapshot generates AI recommendations; the snapshot is intended to provide metrics/context only.

### Team integration checklist
- [ ] Agree on the canonical endpoint paths.
- [ ] Confirm exact Pydantic response shapes.
- [ ] Confirm model fields and migration `0003`.
- [ ] Apply migrations only to the intended database.
- [ ] Verify authentication and tenant isolation.
- [ ] Run all backend tests.
- [ ] Connect the frontend to live API responses.
- [ ] Test empty, loading, error and populated states.
- [ ] Update README and commit/push the final integration changes.

---

## 15. Important known gaps to resolve

Based on the last implementation review, do not mark the full specification complete until these items are checked against the current branch:

1. Required routes `/feedback/analyze`, `/feedback/imports` POST, `/feedback/imports/{id}`, `/feedback/summary`, `/marketing/imports` POST, `/marketing/summary`, `/marketing/timeseries`, `/marketing/breakdown`, and `/analytics/overview` were not all confirmed.
2. Existing route names included `/feedback/import`, `/marketing/import`, and `/analytics/summary`, which differ from the latest required contract.
3. The previously reviewed models used field names such as `saved_rows`/`failed_rows` and had a smaller marketing metric set than the latest specification.
4. The complete dashboard frontend was not verified as implemented.
5. README coverage of every new route, CSV template and final response schema was not verified.
6. The previous test result must be rerun after any new implementation.

**Final integration rule:** The running code, current OpenAPI document, Pydantic schemas, SQLAlchemy models and migration files are the source of truth. This guide explains their intended connections but does not replace verification against the current branch.
