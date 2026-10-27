"""Import every model here so Alembic and Base.metadata can discover them."""

from app.models.business_profile import BusinessProfile  # noqa: F401
from app.models.customer_feedback import CustomerFeedback  # noqa: F401
from app.models.feedback_import import FeedbackImport  # noqa: F401
from app.models.marketing_import import MarketingImport  # noqa: F401
from app.models.marketing_performance import MarketingPerformance  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.strategy import StrategyRun  # noqa: F401
from app.models.recommendation import Outcome, Recommendation, RecommendationStatus  # noqa: F401

__all__ = [
    "User",
    "BusinessProfile",
    "Product",
    "FeedbackImport",
    "CustomerFeedback",
    "MarketingImport",
    "MarketingPerformance",
    "StrategyRun",
    "Recommendation",
    "Outcome",
    "RecommendationStatus",
]
