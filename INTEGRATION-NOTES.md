# Integration notes

This package preserves the original frontend (including login/logout, business profile, onboarding and products) and uses the expanded FastAPI backend containing marketing imports, feedback imports, analytics, strategy generation, recommendations and dashboard APIs.

Important:
- The original frontend's dashboard currently contains illustrative/demo metrics and placeholder sections. The new backend endpoints are available, but the frontend is not yet wired to all of them.
- The original backend `.env` was deliberately not copied because environment files can contain secrets. Configure `backend/.env` locally using `backend/.env.example`.
- Create and activate a fresh virtual environment and install `backend/requirements.txt` before running.
- Review the Alembic migration history before applying migrations to any database with existing data. Back up the database first.
