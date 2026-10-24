from datetime import datetime
from enum import Enum

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    computed_field,
    field_validator,
)

from app.services.onboarding import missing_required_fields

_http_url = TypeAdapter(AnyHttpUrl)


class BusinessModel(str, Enum):
    product = "product"
    service = "service"
    both = "both"


class SalesChannel(str, Enum):
    own_website = "own_website"  # your own online store / website
    marketplace = "marketplace"  # Amazon, Etsy, Flipkart, etc.
    social_commerce = "social_commerce"  # Instagram, Facebook, WhatsApp, etc.
    physical_store = "physical_store"
    wholesale = "wholesale"  # B2B / resellers
    direct_sales = "direct_sales"  # in person, events, referrals
    other = "other"


def _blank_to_none(v: str | None) -> str | None:
    if v is None:
        return None
    v = v.strip()
    return v or None


class BusinessProfileUpsert(BaseModel):
    """Body for PUT /business-profile. Creates the profile or replaces all its fields.

    user_id is never accepted from the client; it comes from the access token.
    """

    business_name: str = Field(min_length=1, max_length=200)
    industry: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=10, max_length=2000)
    business_model: BusinessModel
    sales_channels: list[SalesChannel] = Field(min_length=1, max_length=len(SalesChannel))
    target_audience: str | None = Field(default=None, max_length=2000)
    website_url: str | None = Field(default=None, max_length=2048)
    location: str | None = Field(default=None, max_length=200)
    goals: str | None = Field(default=None, max_length=2000)

    @field_validator("business_name", "industry", "description")
    @classmethod
    def _strip_required(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("target_audience", "location", "goals")
    @classmethod
    def _optional_text(cls, v: str | None) -> str | None:
        return _blank_to_none(v)

    @field_validator("website_url")
    @classmethod
    def _valid_url(cls, v: str | None) -> str | None:
        v = _blank_to_none(v)
        if v is None:
            return None
        try:
            return str(_http_url.validate_python(v))
        except ValidationError:
            raise ValueError("must be a valid http:// or https:// URL")

    @field_validator("sales_channels")
    @classmethod
    def _dedupe_channels(cls, v: list[SalesChannel]) -> list[SalesChannel]:
        return list(dict.fromkeys(v))  # remove duplicates, keep order


class BusinessProfileRead(BaseModel):
    """Saved profile returned to the frontend for display and editing.

    Required-in-the-API fields are optional here only so profiles that predate
    this schema can still be read (and completed) instead of crashing.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    business_name: str
    industry: str
    description: str | None
    business_model: BusinessModel | None
    sales_channels: list[str]
    target_audience: str | None
    website_url: str | None
    location: str | None
    goals: str | None
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def onboarding_completed(self) -> bool:
        return not missing_required_fields(self)


class OnboardingStatus(BaseModel):
    profile_exists: bool
    onboarding_completed: bool
    missing_fields: list[str]
    # "create_business_profile" | "complete_business_profile" | "done"
    next_step: str
