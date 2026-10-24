"""Import every model here so Alembic (and Base.metadata) can see them.

Members 3 and 4: add your model imports below, one line each.
"""
from app.models.business_profile import BusinessProfile  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = ["User", "BusinessProfile", "Product"]
