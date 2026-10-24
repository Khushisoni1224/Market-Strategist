"""Central v1 API router.

HOW TO ADD A NEW MODULE (Members 3 and 4):
  1. Create app/api/v1/endpoints/<your_module>.py exposing `router = APIRouter(prefix="/<path>", tags=[...])`.
  2. Import it below and add ONE line: api_router.include_router(<your_module>.router)
Do not edit Member 2's endpoint modules. This file is shared: keep edits to your own lines
and resolve merge conflicts by keeping everybody's include_router lines.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, business_profile, onboarding, products

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


# --- Member 2: backend foundation ---
api_router.include_router(auth.router)
api_router.include_router(business_profile.router)
api_router.include_router(onboarding.router)
api_router.include_router(products.router)

# --- Member 3 (feedback, analytics): add your include_router lines here ---
# --- Member 4 (strategy, recommendations): add your include_router lines here ---
