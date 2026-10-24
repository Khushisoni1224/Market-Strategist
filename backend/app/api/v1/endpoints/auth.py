from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import CurrentUser, DbSession
from app.core.security import create_access_token
from app.schemas.auth import MeRead, Token, UserCreate, UserRead
from app.services import user_service
from app.services.onboarding import missing_required_fields

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: DbSession):
    if user_service.get_user_by_email(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    try:
        return user_service.create_user(db, payload.email, payload.password)
    except IntegrityError:  # two requests raced past the check above
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    """OAuth2 password flow: send form fields `username` (your email) and `password`."""
    user = user_service.authenticate_user(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=MeRead)
def read_me(current_user: CurrentUser):
    return MeRead(
        **UserRead.model_validate(current_user).model_dump(),
        onboarding_completed=not missing_required_fields(current_user.business_profile),
    )
