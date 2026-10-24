from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator


def _strip_nonblank(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("must not be blank")
    return v


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    inventory_count: int | None = Field(default=None, ge=0)

    _strip = field_validator("name", "category")(_strip_nonblank)


class ProductUpdate(BaseModel):
    """PATCH body: send only the fields you want to change."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    inventory_count: int | None = Field(default=None, ge=0)

    @field_validator("name", "category")
    @classmethod
    def _strip(cls, v: str | None) -> str | None:
        return None if v is None else _strip_nonblank(v)

    @model_validator(mode="after")
    def _no_null_required(self) -> "ProductUpdate":
        for field in ("name", "category", "price"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    category: str
    description: str | None
    price: Decimal
    inventory_count: int | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("price")
    def _price_as_number(self, v: Decimal) -> float:
        return float(v)
