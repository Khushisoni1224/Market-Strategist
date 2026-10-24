from fastapi import APIRouter
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models.business_profile import BusinessProfile
from app.schemas.business_profile import OnboardingStatus
from app.services.onboarding import missing_required_fields, next_step

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/status", response_model=OnboardingStatus)
def onboarding_status(current_user: CurrentUser, db: DbSession):
    """Where is the user in onboarding? Use after login to resume an unfinished setup."""
    profile = db.scalar(select(BusinessProfile).where(BusinessProfile.user_id == current_user.id))
    missing = missing_required_fields(profile)
    return OnboardingStatus(
        profile_exists=profile is not None,
        onboarding_completed=not missing,
        missing_fields=missing,
        next_step=next_step(profile),
    )
