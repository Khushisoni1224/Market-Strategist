# Member 3 — Project Integration Handover
## AI-Powered E-Commerce Marketing Strategist

**Developer responsibility:** Member 3 — Feedback, Privacy & Performance Analytics  
**Current implementation:** Django web application  
**Project directory:** `C:\Users\lenovo\ecommerce-strategist`  
**Virtual environment:** `venv312`  
**Database:** SQLite (`db.sqlite3`)  
**Test status:** 21 automated tests passed in the latest reported run.

---

## 1. Work Completed

### Part A — Customer Feedback Intelligence

Implemented functionality:

- Individual customer feedback submission.
- Sentiment analysis using VADER.
- Sentiment labels and compound scores.
- Customer feedback CSV import.
- CSV validation, including file type, size, required columns and malformed rows.
- Basic masking of email addresses and phone numbers.
- Complaint-theme analysis and dashboard recommendations.
- Feedback import history and individual import-detail pages.
- Import status, row counts, invalid-row counts, and processing error information.
- Database storage of imported feedback and its sentiment results.

**Current limitation:** PII masking is basic and must not be described as perfect anonymization. The feedback workflow also needs additional automated tests and verification of data-quality warnings.

### Part B — Marketing Performance Analytics

Implemented functionality:

- Marketing performance CSV import.
- Validation of required columns, dates, and metric values.
- Storage of marketing performance records.
- Filtering by date range, product, and content type.
- Marketing dashboard with summary cards, charts, and a records table.
- Engagement rate, click-through rate, and conversion rate calculations.
- Handling of missing metric values as `NULL`, rather than automatically converting them to zero.
- Avoidance of rate calculations when required data is missing or denominators are invalid.

The current automated test suite includes tests for valid imports, missing columns, invalid dates, negative values, non-numeric values, malformed rows, empty files, non-CSV files, missing metrics, dashboard loading, filters, and metric calculations.

---

## 2. Django Web Pages and Local URLs

Start the development server:

```cmd
python manage.py runserver
```

Base URL:

`http://127.0.0.1:8000/`

| Page | Local URL | Purpose |
|---|---|---|
| Main Dashboard | `http://127.0.0.1:8000/` | Sentiment summaries, complaint themes, filters and recommendations |
| Submit Feedback | `http://127.0.0.1:8000/feedback/` | Analyze individual customer feedback |
| Import Feedback CSV | `http://127.0.0.1:8000/feedback/import/` | Upload customer feedback |
| Feedback Import History | `http://127.0.0.1:8000/feedback/history/` | Review previous imports and statuses |
| Feedback Import Details | `http://127.0.0.1:8000/feedback/history/<import_id>/` | Review an individual import |
| Marketing Dashboard | `http://127.0.0.1:8000/marketing/` | Marketing summaries, charts, filters and records |
| Import Marketing CSV | `http://127.0.0.1:8000/marketing/import/` | Upload marketing performance data |

**Important:** These are local web-page URLs, not public URLs. They only work while the Django development server is running on the relevant computer. The import-detail URL requires an actual import ID.

---

## 3. Important Project Files

The following file names are based on the Django implementation established during development. Check the actual project directory before preparing a final repository handover.

### Main Django files

| File | Responsibility |
|---|---|
| `manage.py` | Django command-line entry point |
| `ecommerce_sentiment/settings.py` | Project configuration and installed apps |
| `ecommerce_sentiment/urls.py` | Main URL configuration |
| `analyzer/urls.py` | Routes for Member 3 pages |
| `analyzer/views.py` | Dashboard, feedback submission, imports and page logic |
| `analyzer/models.py` | Database models |
| `analyzer/forms.py` | Individual feedback form |
| `analyzer/tests.py` | Automated tests |

### Feedback processing files

| File | Responsibility |
|---|---|
| `analyzer/sentiment.py` | Sentiment analysis functions |
| `analyzer/complaints.py` | Complaint-theme processing |
| `analyzer/feedback_import.py` | Feedback CSV parsing and validation |
| `datasets/clothing_reviews.csv` | Dataset used by the main dashboard |
| `datasets/clothing_reviews_sample.csv` | Sample feedback import dataset |

### Marketing processing files

| File | Responsibility |
|---|---|
| `analyzer/marketing_import.py` | Marketing CSV parsing and validation |
| `analyzer/marketing_metrics.py` | Summary metrics and rate calculations |
| `datasets/marketing_performance_sample.csv` | Sample marketing performance data |

### Templates

| Template | Page |
|---|---|
| `analyzer/templates/analyzer/home.html` | Main dashboard |
| `analyzer/templates/analyzer/feedback.html` | Individual feedback form |
| `analyzer/templates/analyzer/import_feedback.html` | Feedback CSV import |
| `analyzer/templates/analyzer/import_history.html` | Feedback import history |
| `analyzer/templates/analyzer/import_detail.html` | Feedback import details |
| `analyzer/templates/analyzer/import_marketing.html` | Marketing CSV import |
| `analyzer/templates/analyzer/marketing_dashboard.html` | Marketing dashboard |

### Database and dependencies

- `db.sqlite3` — local development database; do not merge this file blindly into the shared production database.
- `analyzer/migrations/0001_initial.py` — initial analyzer database migration.
- `analyzer/migrations/0002_marketingperformance.py` — marketing performance model migration.
- `requirements.txt` — dependency file, if maintained in the project.

The actual migration names, installed packages and files should be confirmed against the current repository before integration.

---

## 4. Database Models

### `FeedbackImport`

Tracks each customer feedback CSV import.

Important fields:

- `filename`
- `status`
- `total_rows`
- `valid_count`
- `invalid_count`
- `analyzed_count`
- `error_message`
- `created_at`

### `CustomerFeedback`

Stores the processed feedback records.

Important fields:

- `import_record`
- `row_number`
- `review_text`
- `sentiment`
- `sentiment_score`
- `created_at`

### `MarketingPerformance`

Stores marketing metrics for each content record.

Identification fields:

- `content_date`
- `content_id`
- `content_type`
- `product_name`

Exposure fields:

- `reach`
- `impressions`
- `views`

Engagement fields:

- `likes`
- `comments`
- `saves`
- `shares`

Traffic fields:

- `profile_visits`
- `clicks`

Business outcome fields:

- `enquiries`
- `conversions`

Metric fields support `NULL` so missing data can remain distinguishable from an actual zero.

---

## 5. API Endpoints Required by the Shared Project Plan

The shared build plan specifies the following endpoints for Member 3. **These are the required API contracts, not confirmed working API URLs in the current Django application.** They must be implemented in, or adapted to, the agreed main backend.

### Feedback API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/feedback/analyze-text` | Analyze submitted feedback |
| POST | `/api/v1/feedback/import` | Start feedback import |
| GET | `/api/v1/feedback/insights` | Return aggregate feedback insights |
| GET | `/api/v1/feedback/imports/{job_id}` | Retrieve import status |

### Performance API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/performance/records` | Create a performance record |
| POST | `/api/v1/performance/import/preview` | Validate and preview an import |
| POST | `/api/v1/performance/import/confirm` | Confirm and process a validated import |
| GET | `/api/v1/performance/imports/{job_id}` | Retrieve import status |
| GET | `/api/v1/performance/summary` | Return aggregate marketing metrics |
| GET | `/api/v1/performance/records` | List performance records |

Once integrated, the base URL will depend on the main backend deployment. For example, if the main backend runs locally on port 8000, the full path might be `http://127.0.0.1:8000/api/v1/feedback/insights`. Do not use that as a working API link until the route is actually registered.

---

## 6. Files and Functions to Hand Over

Provide the main backend integrator with these modules and their dependencies:

**Feedback processing**
- `analyzer/sentiment.py`
- `analyzer/complaints.py`
- `analyzer/feedback_import.py`
- The feedback-related model definitions from `analyzer/models.py`
- Relevant tests from `analyzer/tests.py`

**Marketing processing**
- `analyzer/marketing_import.py`
- `analyzer/marketing_metrics.py`
- The `MarketingPerformance` model definition
- Relevant tests from `analyzer/tests.py`
- `datasets/marketing_performance_sample.csv` as a sample fixture

**Integration references**
- `analyzer/urls.py`
- `analyzer/views.py`
- `analyzer/forms.py`
- The templates, if the team also wants to reuse the Django interface
- The migrations for review by the designated migration integrator

Do not blindly copy all of `settings.py`, `ecommerce_sentiment/urls.py`, or the SQLite database into the main backend. Those files belong to shared application configuration and should be coordinated with the main backend owner.

---

## 7. Integration Requirements and Outstanding Work

Before describing Member 3 as fully integrated, the team should address these items:

1. **Agree on the API contract.** Confirm request formats, response schemas, error formats, nullability, timestamps and pagination with the main backend owner and Member 4.
2. **Adapt the processing logic into the shared backend.** Reuse the sentiment, theme, validation and metric logic rather than copying Django page views directly into API handlers.
3. **Add seller ownership.** Scope private imports, feedback records, performance records and insights to the authenticated seller. The current models shown above do not include seller ownership.
4. **Coordinate migrations.** The shared plan assigns migration coordination to the main backend integrator. Do not independently merge conflicting schema changes.
5. **Add import preview and confirmation.** The current marketing import workflow has validation and saving, but the two-step API preview/confirm contract still needs implementation or an agreed equivalent.
6. **Add comparison and data-quality outputs.** Flag incomplete metrics and small samples; compare periods only when date ranges and metric definitions are clear.
7. **Improve privacy checks.** Avoid logging raw uploaded content, sanitize before model processing, and document the limitations of masking.
8. **Test the integrated workflow.** Run tests after integration, including missing columns, malformed rows, null metrics, authorization and seller ownership.

---

## 8. Test Evidence

Latest reported command:

```cmd
python manage.py test analyzer --verbosity 2
```

Result:

```text
Found 21 test(s).
System check identified no issues (0 silenced).

Ran 21 tests in 0.146s

OK
```

This confirms the reported Django test suite passed in the local development environment. It does not establish that the required `/api/v1/` endpoints, authentication, seller ownership, or full main-backend integration are complete.

---

## 9. Handover Summary for the Main Backend Team

Member 3 has developed a Django-based customer feedback and marketing analytics module. It supports individual feedback analysis, feedback CSV imports, basic PII masking, sentiment scoring, complaint-theme summaries, import history, marketing CSV validation, marketing metric storage, filtered dashboard views, and metric calculations that preserve missing values.

The latest reported local test suite contains 21 passing tests. The main backend team should reuse the processing and validation logic, align the database models and migrations with shared conventions, implement the agreed `/api/v1/` endpoints, add authenticated seller-level access controls, and provide stable structured responses for Member 4's strategy engine.

**Current status:** Core Django functionality implemented and tested; API-contract implementation, authorization, and complete integration remain to be verified or completed.
