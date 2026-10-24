"""TEMPORARY. Member 2 coordinates the real router.py.
Ask them to add these three lines for your modules (see README)."""
from fastapi import APIRouter

from app.api.v1.endpoints import dashboard, recommendations, strategy

api_router = APIRouter()
api_router.include_router(strategy.router)
api_router.include_router(recommendations.router)
api_router.include_router(dashboard.router)
