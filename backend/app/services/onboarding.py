"""Onboarding completeness rules. Single source of truth used by schemas and endpoints."""
from typing import Any

# Fields the user must supply for the portfolio to count as complete.
REQUIRED_FIELDS: tuple[str, ...] = (
    "business_name",
    "industry",
    "description",
    "business_model",
    "sales_channels",
)


def missing_required_fields(profile: Any | None) -> list[str]:
    """Names of required fields that are empty. `profile` may be None (no profile yet)."""
    if profile is None:
        return list(REQUIRED_FIELDS)
    missing = []
    for field in REQUIRED_FIELDS:
        value = getattr(profile, field, None)
        if value is None or (isinstance(value, (str, list)) and len(value) == 0):
            missing.append(field)
    return missing


def next_step(profile: Any | None) -> str:
    if profile is None:
        return "create_business_profile"
    return "complete_business_profile" if missing_required_fields(profile) else "done"
