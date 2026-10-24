"""TEMPORARY. Member 2 owns the real app/main.py. Do NOT commit this file."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401  (registers tables)
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Dev convenience only. The real project uses Alembic migrations (Member 2).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Member 4 - Strategy Engine (standalone dev app)", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
