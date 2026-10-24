import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings

logger = logging.getLogger("market_strategist")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        # DEVELOPMENT ONLY shortcut. Shared/deployed environments must use Alembic migrations.
        from app.db.base import Base
        from app.db.session import engine
        import app.models  # noqa: F401  (registers models on Base.metadata)

        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.project_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(api_router, prefix=settings.api_v1_prefix)
