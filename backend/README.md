# Market-Strategist Backend (Member 2: Foundation, Auth, Business Portfolio, Products)

FastAPI + PostgreSQL + SQLAlchemy 2.x + Alembic + Pydantic 2 + JWT.
Python **3.11+** recommended (3.10 minimum).

## 1. Setup (Windows PowerShell)

```powershell
cd Market-Strategist\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1        # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Generate a secret and paste it into `.env` as `SECRET_KEY`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Database choice
**PostgreSQL (recommended, shared environment):** create an empty database, e.g. in pgAdmin or:
```powershell
psql -U postgres -c "CREATE DATABASE market_strategist;"
```
Then set in `.env`:
`DATABASE_URL=postgresql+psycopg://YOUR_USER:YOUR_PASSWORD@localhost:5432/market_strategist`
(special characters in the password must be URL-encoded, e.g. `@` -> `%40`).

**SQLite (quick local only):** `DATABASE_URL=sqlite:///./dev.db`

## 2. Create tables with Alembic (the standard way)

```powershell
alembic upgrade head          # applies the included initial migration
```
Expected: `Running upgrade  -> 0001, initial schema`

Schema changed later? Edit models, then:
```powershell
alembic revision --autogenerate -m "describe change"
# open the new file in alembic/versions and review it
alembic upgrade head
```
Other commands: `alembic current`, `alembic history`, `alembic downgrade -1`.

> `AUTO_CREATE_TABLES=true` in `.env` creates tables at startup. **Development-only shortcut**; never use it
> in shared environments, and don't mix it with Alembic on the same database (use one or the other).

## 3. Run

```powershell
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs (Swagger UI). Health: http://127.0.0.1:8000/api/v1/health -> `{"status":"ok"}`

## 4. Test in Swagger UI
1. `POST /api/v1/auth/register` -> Try it out -> `{"email":"you@example.com","password":"Passw0rd123"}` -> 201.
2. Click the **Authorize** button (top right). Enter `username` = your **email**, `password` = your password. Leave client_id/secret blank. Authorize -> Close.
3. `GET /api/v1/auth/me` should now return your user.
4. `GET /api/v1/onboarding/status` -> `next_step` is `create_business_profile`.
5. `PUT /api/v1/business-profile` with the example body in section 6, then check `/onboarding/status` again (`done`).
6. Try the `/products` endpoints.

Login uses the OAuth2 password flow: **form-encoded** fields `username` (your email) and `password`, not JSON.

## 5. Automated tests
```powershell
pytest
```
Tests use an in-memory SQLite database and force their own env vars, so they never touch your dev database.
Last run in the build environment: 29 passed (SQLite). The migrations were also applied and checked on a real PostgreSQL 16 server.

## 6. Signup and onboarding flow (business portfolio)

Credentials (`users`) and the business portfolio (`business_profiles`) are separate tables linked one-to-one (`business_profiles.user_id` is unique).

```
1. POST /auth/register          create the account (credentials only)
2. POST /auth/login             get the access token
3. GET  /onboarding/status      or GET /auth/me -> onboarding_completed
      next_step = "create_business_profile"  -> show the portfolio form
      next_step = "complete_business_profile" -> show the form pre-filled (GET /business-profile), fill the missing fields
      next_step = "done"                      -> go to the app
4. PUT  /business-profile       save the portfolio under the logged-in user (full form)
5. GET  /business-profile       later: display and edit (PUT the full form again)
```
**Resuming:** after every login the frontend calls `/onboarding/status` (or reads `onboarding_completed` from `/auth/me`).
If it is not `done`, send the user back to the portfolio form. Closing the browser mid-signup loses nothing: the account exists, and the portfolio is only saved when `PUT` succeeds.
No marketing recommendations are generated at registration or onboarding.

**Portfolio fields** (`PUT /business-profile` body)

| Field | Required | Rules |
|---|---|---|
| `business_name` | yes | brand/entity name, 1-200 chars |
| `industry` | yes | business domain/industry category, 1-100 chars (free text, e.g. "Home decor") |
| `description` | yes | 10-2000 chars |
| `business_model` | yes | `product`, `service` or `both` |
| `sales_channels` | yes | 1+ of `own_website`, `marketplace`, `social_commerce`, `physical_store`, `wholesale`, `direct_sales`, `other` (duplicates removed) |
| `target_audience` | no | up to 2000 chars |
| `website_url` | no | website or public social profile; must be `http://` or `https://` |
| `location` | no | location or target market, up to 200 chars |
| `goals` | no | marketing goals, up to 2000 chars |

Blank optional values are stored as `null`. `user_id` and `id` sent by the client are ignored.

### Shared contract changes (tell Members 1, 3 and 4; they were agreed earlier as the old shape)
- `business_type` is **renamed** `industry`. The migration renames the column and keeps existing data.
- **New required fields:** `description`, `business_model`. **New optional:** `website_url`, `location`.
- `sales_channels` is now a fixed list of codes (above), not free text.
- Profile responses gain `onboarding_completed` (boolean). `/auth/me` gains `onboarding_completed`.
- New endpoint `GET /onboarding/status`.
- Existing rows from before this change keep their data but have empty `description`/`business_model`, so they show as incomplete until the user fills them in.

## 7. API contract (for Member 1 frontend and Members 3/4)

All paths are under `/api/v1`. Protected endpoints need header `Authorization: Bearer <access_token>`.
Errors are JSON: `{"detail": "..."}` (validation errors: `422` with a `detail` list).

| Method | Path | Auth | Body | Success | Errors |
|---|---|---|---|---|---|
| GET | /health | no | - | 200 `{"status":"ok"}` | - |
| POST | /auth/register | no | JSON `{email, password}` | 201 `{id,email,is_active,created_at}` | 409 duplicate, 422 invalid |
| POST | /auth/login | no | **form** `username`(email), `password` | 200 `{access_token, token_type:"bearer"}` | 401 wrong credentials |
| GET | /auth/me | yes | - | 200 user + `onboarding_completed` | 401 |
| GET | /onboarding/status | yes | - | 200 `{profile_exists, onboarding_completed, missing_fields[], next_step}` | 401 |
| GET | /business-profile | yes | - | 200 profile | 404 if none yet, 401 |
| PUT | /business-profile | yes | portfolio fields (section 6) | 200 profile (creates or replaces) | 422, 401 |
| POST | /products | yes | `{name, category, price>0, description?, inventory_count>=0?}` | 201 product | 422, 401 |
| GET | /products | yes | query `category`, `skip`=0, `limit`=50 (max 200) | 200 list | 401 |
| GET | /products/{id} | yes | - | 200 product | 404 (missing or not yours) |
| PATCH | /products/{id} | yes | any subset of product fields | 200 product | 404, 422 |
| DELETE | /products/{id} | yes | - | 204 | 404 |

Profile JSON: `{id, user_id, business_name, industry, description, business_model, sales_channels[], target_audience, website_url, location, goals, created_at, updated_at, onboarding_completed}`.
Product JSON: `{id, user_id, name, category, description, price (number), inventory_count, created_at, updated_at}`.
`PUT /business-profile` replaces all fields: send the whole form each time (omitted optional fields become null).
Frontend note: set `CORS_ORIGINS` in `.env` to your React dev URL (Vite default `http://localhost:5173`).

Example `PUT /business-profile` body:
```json
{
  "business_name": "Cozy Candles",
  "industry": "Home decor",
  "description": "Hand-poured soy candles sold to gift buyers.",
  "business_model": "product",
  "sales_channels": ["marketplace", "social_commerce"],
  "target_audience": "Gift buyers aged 25-40",
  "website_url": "https://instagram.com/cozycandles",
  "location": "India",
  "goals": "Grow repeat customers"
}
```

## 8. For Members 3 and 4: adding your modules (no edits to Member 2 endpoints)
1. Models: create `app/models/<name>.py` (inherit `app.db.base.Base`), add one import line in `app/models/__init__.py`.
   Link to users with `ForeignKey("users.id", ondelete="CASCADE")`; to products with `ForeignKey("products.id", ...)`.
2. Schemas: `app/schemas/<name>.py`. Logic: `app/services/<name>.py`.
3. Endpoints: `app/api/v1/endpoints/<name>.py` with `router = APIRouter(prefix="/<path>", tags=[...])`.
4. Register: one `api_router.include_router(...)` line in `app/api/v1/router.py` (placeholders are marked).
5. Use `CurrentUser` and `DbSession` from `app/core/dependencies.py`; always filter by `user_id == current_user.id`.
6. Need the user's business context for AI prompts? Use `app/services/business_context.py`
   (`get_business_context_for_user(db, user_id)`). It returns the non-empty portfolio fields as a dict, never credentials, and calls no AI.
7. Create your own migration after pulling the latest `main`. The latest revision is `0002`; yours should follow it (see Git section).

### Shared files that need coordination (small, additive edits only; tell the team in the PR)
`requirements.txt`, `app/main.py`, `app/api/v1/router.py`, `app/models/__init__.py`, `.gitignore`, `.env.example`,
`app/schemas/business_profile.py` (enums used by the frontend), and `alembic/versions/*` (two members generating migrations from the same parent create **multiple heads**:
after merging, run `alembic heads`; if more than one, run `alembic merge -m "merge heads" <rev1> <rev2>`).
Renaming any endpoint in the table above breaks the frontend: discuss first.

## 9. Git workflow (never commit to main)

```powershell
git fetch origin
git checkout -b feature/member-2-backend-foundation     # or: git checkout feature/member-2-backend-foundation
# copy/extract the backend folder into the repo root, then:
git status                                               # confirm .env and .venv are NOT listed
git add backend
git commit -m "feat(backend): add FastAPI foundation, auth, business profile and product APIs"
git push -u origin feature/member-2-backend-foundation
```
Open a pull request: on GitHub click **Compare & pull request** for your branch -> base `main` -> add a description
(what changed, how to run, shared files touched) -> request a teammate review. Don't merge your own PR without review.

To stay current: `git fetch origin` then `git merge origin/main` on your branch (resolve conflicts, keep teammates' lines).

## 10. Common errors
| Problem | Fix |
|---|---|
| `ValidationError ... database_url / secret_key Field required` | `.env` missing or not in `backend/`; run commands from `backend/`. |
| `SECRET_KEY must be at least 32 characters` | Generate one with the command in step 1. |
| `password authentication failed` / `connection refused` | Check user/password/port in `DATABASE_URL`; make sure PostgreSQL is running and the DB exists. |
| `relation "users" does not exist` | Run `alembic upgrade head`. |
| `running scripts is disabled` (venv activation) | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `relation ... does not exist` or `column ... does not exist` after pulling | Run `alembic upgrade head` (the portfolio fields are migration `0002`). |
| Swagger login 401 | Use your **email** in the `username` field; register first. |
| `Target database is not up to date` (autogenerate) | Run `alembic upgrade head` first. |
| Browser CORS error from React | Add the React origin to `CORS_ORIGINS`, restart uvicorn. |
