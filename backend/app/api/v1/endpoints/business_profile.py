from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models.business_profile import BusinessProfile
from app.schemas.business_profile import BusinessProfileRead, BusinessProfileUpsert

router = APIRouter(prefix="/business-profile", tags=["business-profile"])


def _get_profile(db, user_id: int) -> BusinessProfile | None:
    return db.scalar(select(BusinessProfile).where(BusinessProfile.user_id == user_id))


@router.get("", response_model=BusinessProfileRead)
def get_business_profile(current_user: CurrentUser, db: DbSession):
    profile = _get_profile(db, current_user.id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Business profile not found")
    return profile


@router.put("", response_model=BusinessProfileRead)
def upsert_business_profile(payload: BusinessProfileUpsert, current_user: CurrentUser, db: DbSession):
    """Create the profile if none exists, otherwise replace its fields.

    Used both for first-time onboarding and for later edits. Send the full form each time.
    """
    data = payload.model_dump(mode="json")  # enums -> plain strings
    profile = _get_profile(db, current_user.id)
    if profile is None:
        profile = BusinessProfile(user_id=current_user.id, **data)
        db.add(profile)
    else:
        for field, value in data.items():
            setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
