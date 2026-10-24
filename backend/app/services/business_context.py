"""Read-only helper for Members 3 and 4.

Turns a user's business portfolio into a plain dict that can be put into an AI
prompt or analytics query as context. It does NOT call any AI and generates no
recommendations.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business_profile import BusinessProfile

_CONTEXT_FIELDS = (
    "business_name",
    "industry",
    "description",
    "business_model",
    "sales_channels",
    "target_audience",
    "website_url",
    "location",
    "goals",
)


def build_business_context(profile: BusinessProfile | None) -> dict[str, object]:
    """Only non-empty fields are included. Never includes user_id, email or credentials."""
    if profile is None:
        return {}
    context: dict[str, object] = {}
    for field in _CONTEXT_FIELDS:
        value = getattr(profile, field)
        if value not in (None, "", []):
            context[field] = value
    return context


def get_business_context_for_user(db: Session, user_id: int) -> dict[str, object]:
    profile = db.scalar(select(BusinessProfile).where(BusinessProfile.user_id == user_id))
    return build_business_context(profile)
